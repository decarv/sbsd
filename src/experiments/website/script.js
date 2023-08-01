let draggedItem = null;
let placeholder = null;

document.querySelectorAll('.draggable').forEach(item => {
  item.addEventListener('dragstart', function(e) {
    draggedItem = this;
    e.dataTransfer.setData('text/plain', this.innerHTML);

    placeholder = document.createElement('div');
    placeholder.classList.add('placeholder');
    this.parentNode.insertBefore(placeholder, this.nextSibling);
  });

  item.addEventListener('dragend', function() {
    draggedItem = null;
    placeholder && placeholder.parentNode.removeChild(placeholder);
  });
});


document.querySelectorAll('#left-column, #right-column').forEach(item => {
  item.addEventListener('dragover', function(e) {
    e.preventDefault();
    const afterElement = getDragAfterElement(this, e.clientY);
    if (afterElement) {
      this.insertBefore(placeholder, afterElement);
    } else {
      this.appendChild(placeholder);
    }
  });

  item.addEventListener('drop', function(e) {
    e.preventDefault();
    if (e.target === this || e.target === getDragAfterElement(this, e.clientY)) {
      const draggable = document.createElement('div');
      draggable.innerHTML = e.dataTransfer.getData('text/plain');
      draggable.classList.add('draggable');
      draggable.setAttribute('draggable', 'true');
      const afterElement = getDragAfterElement(this, e.clientY);
      if (afterElement == null) {
        this.appendChild(draggable);
      } else {
        this.insertBefore(draggable, afterElement);
      }
      if (draggedItem) {
        draggedItem.parentNode.removeChild(draggedItem);
      }
      addDraggableListeners(draggable);
    }
  });
});

function getDragAfterElement(container, y) {
  const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging):not(.placeholder)')];

  return draggableElements.reduce((closest, child) => {
    const box = child.getBoundingClientRect();
    const offset = y - box.top - box.height / 2;
    if (offset < 0 && offset > closest.offset) {
      return { offset: offset, element: child };
    } else {
      return closest;
    }
  }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function addDraggableListeners(el) {
  el.addEventListener('dragstart', function(e) {
    draggedItem = this;
    e.dataTransfer.setData('text/plain', this.innerHTML);
  });

  el.addEventListener('dragend', function() {
    draggedItem = null;
  });
}

document.getElementById('search-button').addEventListener('click', function() {
    const searchQuery = document.getElementById('search-input').value;
    makeRequest(searchQuery);
});

document.getElementById('search-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const searchQuery = this.value;
        makeRequest(searchQuery);
    }
});

function makeRequest(query) {
    fetch(`http://localhost:9000/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            // Handle the data from the response here
            console.log(data);
        })
        .catch(err => {
            // Handle errors here
            console.error(err);
        });
}
