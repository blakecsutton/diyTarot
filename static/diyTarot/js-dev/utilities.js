var utilities = (function() {

  var ELEMENT_NODE = 1;
  var TEXT_NODE = 3;

  // Takes an element node and string for a css class name.
  // Adds the new class to the element without affecting previous classes.
  // Note that this function does not check if the style has already been applied, 
  // however removeStyleClass will work even if a style appears multiple times in the className string.
  function addStyleClass(target, styleClassName) {
    // The extra space is deliberate because then it's always easy to remove a class'
    target.className += ' ' + styleClassName;
  }

  // Takes an element node and a string representing a css class name.
  // If the class is already applied to the element remove it, otherwise make no change.
  function removeStyleClass(target, styleClassName) {
    
    // Matches whitespace followed by a word exactly equal to the class name.
    var styleClassRegExp = new RegExp('\\s\\b' + styleClassName + '\\b', 'g');
    target.className = target.className.replace(styleClassRegExp, ''); 
  }

  /* Simple utility function that accepts an element node and returns a list of its children that are elements. */
  function getElementList(element) {
    
    var nodeList,
        currentNode,
        elementList = [];
        
    nodeList = element.childNodes;
    for( var index = 0; index < nodeList.length; index += 1) {
      
      currentNode = nodeList[index];
      
      if (currentNode.nodeType == ELEMENT_NODE) {
         elementList.push(currentNode);
       }
    }
    
    return elementList;
  }

  // Utility function that searches a list of nodes for element nodes that contain a particular class string
  // in their className. This works for elements with multiple classes, e.g. 'angry hidden monster', however
  // it will also match on cla ss names that targetClass is a substring of. It returns the first result.
  function getChildByClassName(element, targetClass) {
    
    var currentNode;
    var children = element.childNodes;
    
    for ( var ct = 0; ct < children.length; ct += 1 ) {
      
      currentNode = children[ct];
      
      if( currentNode.nodeType == ELEMENT_NODE &&
          currentNode.className.indexOf(targetClass) != -1 ) {
          return currentNode;
      }
    } 
  }
  
  /* Utility function to get a query string parameter from the url by name, or 
   * return false if it isn't there. Example getQueryStringParameter('beer')
   */
  function getQueryStringParameter(name) {
    
    // Can't use a primitive because the regex is built around a variable name.
    var match = RegExp('[?&]' + name + '=([^&]*)')
                    .exec(window.location.search);
    
    // Return false if no match. Replace +'s with spaces and use the decodeURIComponent
    // function to translate any special characters to their equivalents (.e.g, /)
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
  }

  /* Utility function to strip the leading and trailing whitespace from the input string.
   * If the string is nothing but whitespace, it will return "", the empty string.
   */
  function strip(inputString) {
    
    var stripped;
    
    // Strip leading whitespace
    stripped = inputString.replace(/^\s*/g,'');
    // Strip trailing whitespace
    stripped = stripped.replace(/\s*$/g, '');
    
    return stripped;
  }
  
  // Return the functions that you want to be exposed to the rest of the module.
  return {addStyleClass: addStyleClass,
          removeStyleClass: removeStyleClass,
          getElementList: getElementList,
          getQueryStringParameter: getQueryStringParameter};
})();