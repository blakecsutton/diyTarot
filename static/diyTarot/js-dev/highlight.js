window.onload = setup;

function setup() {
  
  function searchAndHighlightNode(currentNode, searchTerm) {
    /* This is a recursive helper function for highlighting a search term in page text.
     * It searches every text node in the tree rooted at the parameter root.
     */
    
      // If the current node is a text node, we can search it and see if we need to
      // highlight anything.
     if(currentNode.nodeType == 3) {
       
       var text = currentNode.nodeValue;
       // Add the i option to make it a case-insensitive match
       var match = RegExp(searchTerm , "i");
       var startIndex = text.search(match);
       
       // If the search term appears in the text, then we have to split the text 
       // across multiple nodes to highlight it.
       if( startIndex > -1 ) {
         
         // This is the slice of the string which matches the search term
         // Have to get it from the original text, not the search term, because it's
         // a case-insensitive search.
         var beforeText = text.slice(0, startIndex);
         var searchText = text.slice(startIndex, startIndex + searchTerm.length );
         var afterText = text.slice(startIndex + searchTerm.length);
         
         // Get the parent node and remove the current node from the tree, since we're replacing
         // it with 2-3 nodes instead.
         parentNode = currentNode.parentElement;
         var sibling = null;
         if( currentNode.nextSibling ) {
           sibling = currentNode.nextSibling;
         }
         parentNode.removeChild(currentNode);
         
         // Create the styled span element that holds the match to the search term.
         var highlightedNode = document.createElement("span");
         highlightedNode.className = "search-highlight";
         var highlightedTextNode = document.createTextNode(searchText);
         highlightedNode.appendChild( highlightedTextNode );
         
         // Handle the different cases of where the search term is found in the string:
         // The beginning, the middle, and the end.
         var beforeNode, afterNode;
         if(beforeText.length == 0 ) {
           // Case 1: search term is at the start of the string, so slice would be ["", "finish""]
           
           afterNode = document.createTextNode(afterText);
     
           // Now actually insert the new nodes, in order, in the same place the old node was.
           if( sibling ) {
             parentNode.insertBefore(afterNode, sibling);
             parentNode.insertBefore(highlightedNode, afterNode);
           }
           else {
             parentNode.appendChild(highlightedNode);
             parentNode.appendChild(afterNode);
           }
         }
         else if( afterText.length == 0 ) {
           // Case 2: search term is at end of string, so slice would be ["start", ""]
           beforeNode = document.createTextNode(beforeText);
           
           // Now actually insert the new nodes, in order, in the same place the old node was.
           if( sibling ) {
             parentNode.insertBefore(highlightedNode, sibling);
             parentNode.insertBefore(beforeNode, highlightNode);
           }
           else {
             parentNode.appendChild(beforeNode);
             parentNode.appendChild(highlightedNode);
           }
           
         }
         else {
           // Case 3: search term is at the middle of the string, so slice would be ["start", "finish"]
           beforeNode = document.createTextNode(beforeText);
           afterNode = document.createTextNode(afterText);
          
           // Now actually insert the new nodes, in order, in the same place the old node was.
           if( sibling ) {
             parentNode.insertBefore(afterNode, sibling);
             parentNode.insertBefore(highlightedNode, afterNode);
             parentNode.insertBefore(beforeNode, highlightedNode);
           }
           else {
             parentNode.appendChild(beforeNode);
             parentNode.appendChild(highlightedNode);
             parentNode.appendChild(afterNode);
           }
         }
  
       }
       
     }
     else if( currentNode.nodeType == 1 ){
       // Otherwise, if we are processing an element node there's nothing to do but
       // recurse on the children, looking for text nodes to search.
       for(var index = 0; index < currentNode.childNodes.length; index += 1) {
         searchAndHighlightNode(currentNode.childNodes[index], searchTerm);
       }    
     }
     
  }
  
  // There is no interactivity in the app right now, all we're doing is highlighting search terms.
  //console.log("there was a search so I'm in the template!");
 
  // This script is only included if there was a search made, so for now we don't have to worry 
  // about checking if we should highlight or not.

 // Get the actual search term for comparison purposes.
 var searchTerm = utilities.getQueryStringParameter('search');
 
 // Pull all the header elements in the document (contains the card title)
 var headers = document.getElementsByClassName('header');
 
 var index;
 for(index = 0; index < headers.length; index += 1) {
   // Walk the subtree rooted at each header element searching and highlighting text.
   searchAndHighlightNode(headers[index], searchTerm);
 }
 
 var cardTexts = document.getElementsByClassName('card_text');
 for(index = 0; index < cardTexts.length; index += 1) {
   searchAndHighlightNode(cardTexts[index], searchTerm);
 }
}


  
 



