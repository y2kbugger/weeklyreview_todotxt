/**
 * Handles backspace key events and triggers a delete request via htmx
 * @param {Event} event - The input event
 */
function handleKeyDown(event) {
    if (event.key === 'Backspace') {
        if (event.target.tagName === 'LI' && event.target.classList.contains('list-item')) {
            //## Delete list item on Backspace key press ##//


            // dont delete if li has text
            if (event.target.innerText.trim() != '') { return; }

            event.preventDefault();

            // dont delete if it is the only li in ul
            const ul = event.target.closest('ul');
            const all_list_items = ul.querySelectorAll('li.list-item');
            if (all_list_items.length <= 1) { return; }

            const itemId = event.target.dataset.id;

            const prevLi = event.target.previousElementSibling;
            htmx.ajax('DELETE', `/xxx/list/item/${itemId}`, {
                target: event.target,
                event: event,
                swap: 'delete'
            }).then(() => {
                // focus previous li.list-item in ul, with cursor at the end
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
            });
        }
    } else if (event.key === 'Enter') {
        if (event.target.tagName === 'LI' && event.target.classList.contains('list-item')) {
            //## Create a new list item on Enter key press ##//

            // if shift is pressed, inssert a \n otherwise create a new li
            if (event.shiftKey) {
                return;
            } else {
                // prevent default enter behavior
                event.preventDefault();
            }

            // if li is already a blank line, don't create a new one
            if (event.target.innerText.trim() === '') { return; }


            // create a new li.list-item after the current one
            htmx.ajax('POST', `/xxx/list/item`, {
                source: event.target,
                event: event,
                swap: 'afterend',
                target: event.target,
                values: {
                    after_item_id: event.target.dataset.id,
                }
            }).then(() => {
                newLi = event.target.nextElementSibling;
                if (newLi && newLi.tagName === 'LI' && newLi.classList.contains('list-item')) {
                    // focus the new li.list-item
                    newLi.focus();
                }
            });
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
