// bst.h
#ifndef BST_H
#define BST_H

struct node {
    int key;
    struct node* left;
    struct node* right;
};

// Function declarations
struct node* newNode(int data);
struct node* insert(struct node* node, int data);
struct node* deleteNode(struct node* root, int data);
int search(struct node* root, int data);
struct node* minValueNode(struct node* node);
struct node* maxValueNode(struct node* node);  // Add this declaration
int isValidBST(struct node* node);             // Add this declaration
void freeTree(struct node* node);              // Add this declaration

#endif
