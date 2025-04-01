/**
 * Handles keydown events for list item textareas
 * @param {Event} event - The keydown event
 */
function handleKeyDownFromTxt(event) {
    if (event.target.tagName !== 'TEXTAREA') return;
    if (!event.target.closest('li.list-item')) return;

    const listItem = event.target.closest('li.list-item');
    const txt = event.target;

    // Auto-resize is now handled by input event instead of keydown

    if (event.key === 'Backspace' && txt.value === '') {
        // Don't delete if there's no listitem before current one
        const prevLi = listItem.previousElementSibling;
        if (!prevLi || !prevLi.classList.contains('list-item')) return;

        event.preventDefault();
        htmx.ajax('DELETE', `/xxx/list/item/${listItem.dataset.id}`, {
            target: listItem,
            event: event,
            swap: 'delete'
        }).then(() => {
            // Focus previous textarea in li.list-item, with cursor at the end
            const prevTxt = prevLi.querySelector('textarea');
            if (prevTxt) {
                prevTxt.focus();
                prevTxt.selectionStart = prevTxt.selectionEnd = prevTxt.value.length;
            }
        });
        return;
    }

    // Handle Enter to create new item
    if (event.key === 'Enter' && !event.shiftKey) {
        // Prevent default enter behavior
        event.preventDefault();

        htmx.ajax('POST', `/xxx/list/item`, {
            source: listItem,
            event: event,
            swap: 'afterend',
            target: listItem,
            values: {
                after_item_id: listItem.dataset.id,
            }
        }).then(() => {
            const newLi = listItem.nextElementSibling;
            if (newLi && newLi.classList.contains('list-item')) {
                // Focus the new textarea
                const newTextarea = newLi.querySelector('textarea');
                if (newTextarea) {
                    newTextarea.focus();
                }
            }
        });
    }
}

/**
 * Auto-resize textarea to fit content
 * @param {HTMLTextAreaElement} textarea - The textarea to resize
 */
function autoResizeTextarea(textarea) {
    // Reset height to auto so scrollHeight doesn't include previous manually set height
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

/**
 * Setup swipe to delete functionality using Hammer.js
 */
function setupSwipeToDelete() {
    document.querySelectorAll('li.list-item').forEach(setupItemSwipe);

    // Setup mutation observer to handle dynamically added items
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1 && node.matches('li.list-item')) {
                        setupItemSwipe(node);
                    }
                });
            }
        });
    });

    observer.observe(document.querySelector('main'), {
        childList: true,
        subtree: true
    });
}

/**
 * Setup swipe for a specific list item
 * @param {HTMLElement} listItem - The list item element
 */
function setupItemSwipe(listItem) {
    const hammer = new Hammer(listItem);

    // Configure horizontal swipe detection
    hammer.get('swipe').set({ direction: Hammer.DIRECTION_HORIZONTAL });

    // Define swipe threshold and variables
    const SWIPE_THRESHOLD = -80; // Left swipe threshold
    let currentX = 0;
    let startX = 0;
    let isDragging = false;

    // Handle pan start
    hammer.on('panstart', function (e) {
        isDragging = true;
        startX = 0;
        listItem.classList.add('swiping');
        listItem.style.transition = '';
    });

    // Handle panning
    hammer.on('pan', function (e) {
        if (!isDragging) return;

        currentX = e.deltaX;
        // Only allow left swipe
        if (currentX <= 0) {
            // Add resistance as user swipes further
            const distance = Math.min(0, currentX);
            const opacity = 1 - (Math.abs(distance) / 300);

            listItem.style.transform = `translateX(${distance}px)`;
            listItem.style.opacity = Math.max(0.7, opacity);

            // Show delete indicator when swiping past threshold
            if (currentX < SWIPE_THRESHOLD) {
                listItem.classList.add('swipe-delete-ready');
            } else {
                listItem.classList.remove('swipe-delete-ready');
            }
        }
    });

    // Handle pan end
    hammer.on('panend', function (e) {
        if (!isDragging) return;
        isDragging = false;

        listItem.style.transition = 'transform 0.3s ease, opacity 0.3s ease';

        if (currentX < SWIPE_THRESHOLD) {
            // Swiped far enough - complete the delete action
            listItem.style.transform = 'translateX(-100%)';
            listItem.style.opacity = '0';

            // Process deletion after animation
            setTimeout(() => {
                try {
                    htmx.ajax('DELETE', `/xxx/list/item/${listItem.dataset.id}`, {
                        target: listItem,
                        swap: 'delete'
                    }).then(() => {
                        // Focus previous textarea if exists
                        const prevLi = listItem.previousElementSibling;
                        if (prevLi && prevLi.classList.contains('list-item')) {
                            const prevTxt = prevLi.querySelector('textarea');
                            if (prevTxt) {
                                prevTxt.focus();
                                prevTxt.selectionStart = prevTxt.selectionEnd = prevTxt.value.length;
                            }
                        }
                    }).catch(error => {
                        console.error('Error deleting item:', error);
                        // Reset if delete fails
                        listItem.style.transform = 'translateX(0)';
                        listItem.style.opacity = '1';
                    });
                } catch (err) {
                    console.error('Error processing delete:', err);
                    // Reset on error
                    listItem.style.transform = 'translateX(0)';
                    listItem.style.opacity = '1';
                }
            }, 300);
        } else {
            // Not swiped far enough - revert
            listItem.style.transform = 'translateX(0)';
            listItem.style.opacity = '1';
        }

        listItem.classList.remove('swiping', 'swipe-delete-ready');
    });
}

// Attach event listeners
document.addEventListener('DOMContentLoaded', function () {
    // Load Hammer.js dynamically
    const hammerScript = document.createElement('script');
    hammerScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js';
    hammerScript.onload = function () {
        // Initialize swipe only after Hammer.js is loaded
        setupSwipeToDelete();
    };
    document.head.appendChild(hammerScript);

    const main = document.querySelector('main');
    if (main) {
        main.addEventListener('keydown', handleKeyDownFromTxt);

        // Add input event listener for auto-resizing
        main.addEventListener('input', function (event) {
            if (event.target.tagName === 'TEXTAREA' && event.target.closest('li.list-item')) {
                autoResizeTextarea(event.target);
            }
        });

        // Initialize height for all existing textareas
        document.querySelectorAll('li.list-item textarea').forEach(autoResizeTextarea);
    }
});
