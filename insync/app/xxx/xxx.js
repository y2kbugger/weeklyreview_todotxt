/**
 * Handles keydown events for list item textareas
 * @param {Event} event - The keydown event
 */
function handleKeyDownFromTxt(event) {
    if (event.target.tagName !== 'TEXTAREA') return;
    if (!event.target.closest('li.list-item')) return;

    const listItem = event.target.closest('li.list-item');
    const txt = event.target;

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

// Attach event listeners
document.addEventListener('DOMContentLoaded', function () {
    const main = document.querySelector('main');
    if (main) {
        main.addEventListener('keydown', handleKeyDownFromTxt);
    }
});
