import pickle

class BSTNode:
  """
  A utility class for BSTs.
  """
  def __init__(self, token_list):
    """__init__.
    Constructor.
    Creates a balanced BST from the list of tokens token_list.
    :param token_list: A list of tokens.
    """
    #token list is a nonempty, sorted list of token strings
    mid = len(token_list)//2
    self.l = self.r = None
    self.val = token_list[mid]
    if mid!=0:
      self.l = BSTNode(token_list[:mid])
    if len(token_list)>1 and mid !=len(token_list)-1:
      self.r = BSTNode(token_list[mid+1:])

  def search(self, string):
    """search.
    A lower bound function. Finds the lower bound for the element "string"
    in the tree rooted at this node.
    :param string: A query term string
    """

    if self.val == string:
      return self
    if self.val > string:
      if self.l is None:
        return self
      return self.l.search(string) or self
    else:
      if self.r is None:
        return None
      return self.r.search(string)

  
  def minValue(self):
      """minValue.
        A helper function that returns the minimum value in the current subtree.
      """
      current = self
      # loop down to find the leftmost leaf 
      while(current is not None):
          if current.l is None:
              break
          current = current.l
      return current

  def inOrderSuccessor(self, n):
      """
      A helper function that returns the inOrderSuccessor of the element n.
      In the tree rooted at this node.
      """
      if n.r is not None:
          return n.r.minValue()
      root = self
      succ=None
      while(root):
          if(root.val<n.val):
              root=root.r
          elif(root.val>n.val):
              succ=root
              root=root.l
          else:
              break
      return succ
