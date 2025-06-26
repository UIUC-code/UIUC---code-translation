// bst.c - Enhanced BST implementation
#include "bst.h"
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
// Create a new BST node
struct node* newNode(int key) {
    struct node* temp = (struct node*)malloc(sizeof(struct node));
    if (temp == NULL) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }
    temp->key = key;
    temp->left = NULL;
    temp->right = NULL;
    return temp;
}

// Insert a node into BST
struct node* insert(struct node* node, int key) {
    if (node == NULL)
        return newNode(key);

    if (key < node->key)
        node->left = insert(node->left, key);
    else if (key > node->key)
        node->right = insert(node->right, key);
    
    return node;
}

// Search for a key in BST
int search(struct node* root, int key) {
    if (root == NULL) return 0;
    
    if (key == root->key) 
        return 1;
    else if (key < root->key)
        return search(root->left, key);
    else
        return search(root->right, key);
}

// Find node with minimum value
struct node* minValueNode(struct node* node) {
    struct node* current = node;
    while (current && current->left != NULL)
        current = current->left;
    return current;
}

// Find node with maximum value
struct node* maxValueNode(struct node* node) {
    struct node* current = node;
    while (current && current->right != NULL)
        current = current->right;
    return current;
}

// Delete a node from BST
struct node* deleteNode(struct node* root, int key) {
    if (root == NULL) return root;

    if (key < root->key)
        root->left = deleteNode(root->left, key);
    else if (key > root->key)
        root->right = deleteNode(root->right, key);
    else {
        // Node with one child or no child
        if (root->left == NULL) {
            struct node* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            struct node* temp = root->left;
            free(root);
            return temp;
        }

        // Node with two children
        struct node* temp = minValueNode(root->right);
        root->key = temp->key;
        root->right = deleteNode(root->right, temp->key);
    }
    return root;
}

// Helper function for BST validation
int isBSTUtil(struct node* node, int min, int max) {
    if (node == NULL) return 1;
    
    if (node->key < min || node->key > max)
        return 0;
        
    return isBSTUtil(node->left, min, node->key-1) && 
           isBSTUtil(node->right, node->key+1, max);
}

// Validate BST properties
int isValidBST(struct node* root) {
    return isBSTUtil(root, INT_MIN, INT_MAX);
}

// Free memory allocated for BST
void freeTree(struct node* node) {
    if (node == NULL) return;
    freeTree(node->left);
    freeTree(node->right);
    free(node);
}

// Inorder traversal (for debugging)
void inorder(struct node* root) {
    if (root != NULL) {
        inorder(root->left);
        printf("%d ", root->key);
        inorder(root->right);
    }
}

/* The main function is commented out as we'll be using klee_test.c
int main() {
    // Test code remains here
} */
