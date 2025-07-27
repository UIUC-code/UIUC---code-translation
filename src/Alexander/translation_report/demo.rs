use std::cmp::Ordering;

// 定义二叉树节点
#[derive(Debug)]
struct Node {
    key: i32,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

impl Node {
    // 创建新节点
    fn new(key: i32) -> Self {
        Node {
            key,
            left: None,
            right: None,
        }
    }

    // 中序遍历
    fn inorder_traversal(&self) {
        if let Some(left) = &self.left {
            left.inorder_traversal();
        }
        print!("{} ", self.key);
        if let Some(right) = &self.right {
            right.inorder_traversal();
        }
    }

    // 插入节点
    fn insert(&mut self, key: i32) {
        if key < self.key {
            if let Some(left) = &mut self.left {
                left.insert(key);
            } else {
                self.left = Some(Box::new(Node::new(key)));
            }
        } else {
            if let Some(right) = &mut self.right {
                right.insert(key);
            } else {
                self.right = Some(Box::new(Node::new(key)));
            }
        }
    }

    // 查找最小节点
    fn min_value_node(node: &Node) -> i32 {
        let mut current = node;
        while let Some(left) = &current.left {
            current = left;
        }
        current.key
    }

    // 删除节点 (返回新的根节点)
    fn delete_node(root: Option<Box<Node>>, key: i32) -> Option<Box<Node>> {
        let mut root_node = match root {
            Some(node) => node,
            None => return None,
        };

        match key.cmp(&root_node.key) {
            Ordering::Less => {
                root_node.left = Node::delete_node(root_node.left, key);
                Some(root_node)
            }
            Ordering::Greater => {
                root_node.right = Node::delete_node(root_node.right, key);
                Some(root_node)
            }
            Ordering::Equal => {
                // 处理节点的三种删除情况
                match (root_node.left.take(), root_node.right.take()) {
                    (None, None) => None, // 无子节点
                    (Some(left), None) => Some(left), // 只有左子节点
                    (None, Some(right)) => Some(right), // 只有右子节点
                    (Some(left), Some(right)) => { // 有两个子节点
                        // 找到右子树的最小值
                        let min_key = Node::min_value_node(&right);
                        
                        // 删除右子树中的最小节点
                        let new_right = Node::delete_node(Some(right), min_key);
                        
                        // 创建新节点
                        Some(Box::new(Node {
                            key: min_key,
                            left: Some(left),
                            right: new_right,
                        }))
                    }
                }
            }
        }
    }
}

fn main() {
    // 创建根节点
    let mut root = Some(Box::new(Node::new(50)));
    
    // 插入节点
    if let Some(ref mut node) = root {
        node.insert(30);
        node.insert(20);
        node.insert(40);
        node.insert(70);
        node.insert(60);
        node.insert(80);
    }

    // 中序遍历
    println!("Inorder traversal of the given tree:");
    if let Some(ref node) = root {
        node.inorder_traversal();
    }
    println!();

    // 删除节点 20
    println!("Delete 20");
    root = Node::delete_node(root, 20);
    println!("Inorder traversal of the modified tree:");
    if let Some(ref node) = root {
        node.inorder_traversal();
    }
    println!();

    // 删除节点 30
    println!("Delete 30");
    root = Node::delete_node(root, 30);
    println!("Inorder traversal of the modified tree:");
    if let Some(ref node) = root {
        node.inorder_traversal();
    }
    println!();

    // 删除节点 50
    println!("Delete 50");
    root = Node::delete_node(root, 50);
    println!("Inorder traversal of the modified tree:");
    if let Some(ref node) = root {
        node.inorder_traversal();
    }
    println!();
}