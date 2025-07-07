#include <stdio.h>
#include <string.h>
#include <stdlib.h>


typedef enum
{
    BOOL,
    INT,
    STRING
} ParamType;

typedef struct ConfigVar
{
    const char *name;
    ParamType type;
    union
    {
        int int_val;
        int bool_val; 
        char *str_val;
    } value;
    struct ConfigVar *next; 
} ConfigVar;

ConfigVar *all_sys_vars = NULL;


ConfigVar *create_var(const char *name, ParamType type, void *value)
{
    ConfigVar *var = (ConfigVar *)malloc(sizeof(ConfigVar));
    if (!var)
    {
        perror("Failed to allocate memory for new variable");
        exit(EXIT_FAILURE);
    }

    var->name = name;
    var->type = type;
    switch (type)
    {
    case INT:
        var->value.int_val = *(int *)value;
        break;
    case BOOL:
        var->value.bool_val = *(int *)value;
        break;
    case STRING:
        var->value.str_val = (char *)value;
        break;
    }
    var->next = NULL;
    return var;
}

ConfigVar *get_config_var(const char *name)
{
    ConfigVar *current = all_sys_vars;
    while (current != NULL)
    {
        if (strcmp(current->name, name) == 0)
        {
            return current;
        }
        current = current->next;
    }
    return NULL; 
}

static char *trim(char *s)
{
    while (*s && (*s == ' ' || *s == '\t' || *s == '\n' || *s == '\r'))
        ++s; 
    if (*s == 0)
        return s; 
    char *end = s + strlen(s) - 1;
    while (end > s && (*end == ' ' || *end == '\t' || *end == '\n' || *end == '\r'))
        *end-- = '\0'; 
    return s;
}

void parse_config_file(const char *filename)
{
    FILE *fp = fopen(filename, "r");
    if (!fp)
    {
        perror("Could not open config file");
        exit(EXIT_FAILURE);
    }

    char line[256];
    while (fgets(line, sizeof(line), fp))
    {
        if (line[0] == '#' || line[0] == '\n')
            continue;

        char *eq = strchr(line, '=');
        if (!eq)
            continue; 
        *eq = '\0';
        char *key = trim(line);
        char *val = trim(eq + 1);

        val[strcspn(val, "\n\r")] = 0;

        char *key_dup = malloc(strlen(key) + 1);
        if (!key_dup)
        {
            perror("malloc");
            exit(EXIT_FAILURE);
        }
        strcpy(key_dup, key);

        if (strcmp(key, "binlog_format") == 0)
        {
            char *dup = malloc(strlen(val) + 1);
            if (!dup)
            {
                perror("malloc");
                exit(EXIT_FAILURE);
            }
            strcpy(dup, val);
            ConfigVar *var = create_var(key_dup, STRING, dup);
            var->next = all_sys_vars;
            all_sys_vars = var;
        }
        else if (strcmp(key, "autocommit") == 0 || strcmp(key, "flush_at_trx_commit") == 0)
        {
            int b = atoi(val);
            ConfigVar *var = create_var(key_dup, BOOL, &b);
            var->next = all_sys_vars;
            all_sys_vars = var;
        }
        else if (strcmp(key, "query_cache_size") == 0)
        {
            int i = atoi(val);
            ConfigVar *var = create_var(key_dup, INT, &i);
            var->next = all_sys_vars;
            all_sys_vars = var;
        }
        else
        {
            free(key_dup);
        }
    }
    fclose(fp);
}


void perform_light_commit()
{
    printf("Executing LIGHT commit: Caching transaction to commit later.\n");
    for (volatile int i = 0; i < 1000; i++)
        ;
}

void perform_standard_commit()
{
    printf("Executing STANDARD commit: Committing to memory.\n");
    for (volatile int i = 0; i < 100000; i++)
        ;
}

void perform_heavy_flush_commit()
{
    printf("Executing HEAVY commit: Flushing transaction to disk immediately.\n");
    for (volatile int i = 0; i < 500000; i++)
        ;
}

void write_row_to_log()
{
    printf("\nA 'write_row' operation has been requested.\n");

    ConfigVar *binlog_format = get_config_var("binlog_format");
    ConfigVar *autocommit = get_config_var("autocommit");
    ConfigVar *flush_at_trx_commit = get_config_var("flush_at_trx_commit");

    if (binlog_format && strcmp(binlog_format->value.str_val, "ROW") == 0)
    {
        printf("-> Binlog format is 'ROW'. Checking autocommit status.\n");

        if (autocommit && autocommit->value.bool_val == 1)
        {
            printf("--> Autocommit is ON. Transaction will be committed now.\n");

            if (flush_at_trx_commit && flush_at_trx_commit->value.bool_val == 1)
            {
                printf("---> flush_at_trx_commit is ON.\n");
                perform_heavy_flush_commit(); 
            }
            else
            {
                printf("---> flush_at_trx_commit is OFF.\n");
                perform_standard_commit(); 
            }
        }
        else
        {
            printf("--> Autocommit is OFF.\n");
            perform_light_commit(); 
        }
    }
    else
    {
        printf("-> Binlog format is not 'ROW'. Logging is minimal. No commit action taken.\n");
    }
}

void setup_query_cache()
{
    ConfigVar *cache_size = get_config_var("query_cache_size");
    if (cache_size && cache_size->value.int_val > 8000)
    {
        printf("\nSetting up a LARGE query cache buffer (%d bytes).\n", cache_size->value.int_val);
    }
    else
    {
        printf("\nSetting up a standard query cache buffer.\n");
    }
}


int main(int argc, char *argv[])
{
    const char *config_path = (argc > 1) ? argv[1] : "config.txt";

    parse_config_file(config_path);

    printf("Configuration parsing complete. Current values are:\n");
    printf("- binlog_format: %s\n", get_config_var("binlog_format") ? get_config_var("binlog_format")->value.str_val : "<unset>");
    printf("- autocommit: %d\n", get_config_var("autocommit") ? get_config_var("autocommit")->value.bool_val : -1);
    printf("- flush_at_trx_commit: %d\n", get_config_var("flush_at_trx_commit") ? get_config_var("flush_at_trx_commit")->value.bool_val : -1);
    printf("- query_cache_size: %d\n", get_config_var("query_cache_size") ? get_config_var("query_cache_size")->value.int_val : -1);

    write_row_to_log();
    setup_query_cache();

    ConfigVar *cur = all_sys_vars;
    while (cur)
    {
        ConfigVar *next = cur->next;
        if (cur->type == STRING)
            free(cur->value.str_val);
        free((void *)cur->name);
        free(cur);
        cur = next;
    }

    return 0;
}
