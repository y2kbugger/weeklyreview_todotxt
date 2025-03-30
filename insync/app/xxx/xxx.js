/**
 * Handles backspace key events and triggers a delete request via htmx
 * @param {Event} event - The input event
 */
function handleKeyDown(event) {
    if (event.key === 'Backspace') {
        if (event.target.tagName === 'LI' && event.target.classList.contains('list-item')) {
            // dont delete if li has text
            if (event.target.innerText.trim() != '') { return; }

            // dont delete if it is the only li in ul
            const ul = event.target.closest('ul');
            const all_list_items = ul.querySelectorAll('li.list-item');
            console.log(all_list_items);
            if (all_list_items.length <= 1) { return; }

            const itemId = event.target.dataset.id;

            htmx.ajax('DELETE', `/xxx/list/item/${itemId}`, {
                source: event.target,
                event: event,
                swap: 'delete'
            });

            // focus previous li.list-item in ul, with cursor at the end
            const prevLi = event.target.previousElementSibling;
            if (prevLi && prevLi.classList.contains('list-item')) {
                prevLi.focus();

                // Place cursor at the end of the editable content
                const range = document.createRange();
                const selection = window.getSelection();
                range.selectNodeContents(prevLi);
                range.collapse(false); // false means collapse to end
                selection.removeAllRanges();
                selection.addRange(range);
            } else {
                // focus the ul if there is no previous li
                ul.focus();
            }
            event.preventDefault();
        }
    }
}

// Attach the handleKeyDown event listener to the main element
document.addEventListener('DOMContentLoaded', function () {
    const main = document.querySelector('main');
    if (main) {
        main.addEventListener('keydown', handleKeyDown);
    }
});
