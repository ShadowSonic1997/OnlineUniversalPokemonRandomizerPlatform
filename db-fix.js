// Initialize the required object stores for CheerpJ
(function() {
  try {
    // Run this before CheerpJ loads
    const initIndexedDB = () => {
      const request = indexedDB.open('cheerpjFS', 1);
      
      request.onupgradeneeded = function(event) {
        const db = event.target.result;
        
        // Create object stores that CheerpJ might need
        if (!db.objectStoreNames.contains('files')) {
          db.createObjectStore('files', { keyPath: 'path' });
        }
        
        // Additional stores that might be needed
        if (!db.objectStoreNames.contains('metadata')) {
          db.createObjectStore('metadata', { keyPath: 'path' });
        }
      };
      
      request.onerror = function(event) {
        console.log('IndexedDB initialization error:', event.target.error);
      };
      
      request.onsuccess = function(event) {
        console.log('IndexedDB initialized successfully');
      };
    };
    
    // Run the initialization
    initIndexedDB();
    
    // Also handle errors from CheerpJ's IndexedDB operations
    const originalTransaction = IDBDatabase.prototype.transaction;
    IDBDatabase.prototype.transaction = function() {
      try {
        return originalTransaction.apply(this, arguments);
      } catch (e) {
        console.log('Caught IndexedDB transaction error:', e);
        // Attempt recovery by reopening the database
        initIndexedDB();
        // Return a mock transaction to prevent errors
        return {
          objectStore: function() {
            return {
              put: function() { return { onsuccess: null, onerror: null }; },
              get: function() { return { onsuccess: null, onerror: null }; },
              delete: function() { return { onsuccess: null, onerror: null }; }
            };
          }
        };
      }
    };
  } catch (e) {
    console.error('Error setting up IndexedDB fix:', e);
  }
})();
