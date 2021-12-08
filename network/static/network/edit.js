function edit(event) {
    const edit_btn = event.target;
    const container = event.target.parentElement;
    const post_content = container.querySelector('.post-content');
    post_content.style.display = 'none';
    
    const textarea = document.createElement('textarea');
    textarea.cols = 50;
    textarea.rows = 5;
    textarea.placeholder = 'Edit your post';
    textarea.value = post_content.innerHTML.replaceAll('<br>', '\n');

    edit_btn.style.display = 'none';
    const save_button = document.createElement('button');
    save_button.classList.add('btn', 'btn-primary', 'btn-sm', 'mt-2');
    save_button.id = 'save-btn';
    save_button.innerHTML = 'Save';
    container.append(save_button);
    save_button.onclick = () => {
        fetch('/edit', {
            method: "POST",
            body: JSON.stringify({
                content: textarea.value,
                post_id: container.dataset.post_id
            }),
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
            save_button.remove();
            edit_btn.style.display = 'block';
            if (result.status === '200') {
                post_content.innerText = textarea.value;
            }
            post_content.style.display = 'block';
            textarea.remove();
        });
    };
    
    container.insertBefore(textarea, post_content);


}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function like(event) {
    const container = event.target.parentElement;
    const like_btn = container.querySelector('.like-btn')
    fetch('/like', {
        method: "POST",
        body: JSON.stringify({
            'post_id': container.dataset.post_id,
            'liked': like_btn.dataset.liked
        }),
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (response.status === 403) {
            alert('You must be logged in to like the post!');
            throw new Error('Not logged in');
        }
        return response.json();
    })
    .then(result => {
        alert(result.message);
        like_btn.dataset.liked = result.liked;
        if (result.liked == 'true') {
            like_btn.innerHTML = `❤ ${result.likes}<br>`;
        } else {
            like_btn.innerHTML = `\u2661 ${result.likes}<br>`;
        }
        listen_likes(like_btn);
    })
    .catch(error => {
        console.log(error);
    });
}

function listen_likes(like_btn) {
    if (like_btn.dataset.liked == 'true') {
        like_btn.onmouseover = (event) => {event.target.innerHTML = `\u2661 ${event.target.innerHTML.slice(2)}`;};
        like_btn.onmouseleave = (event) => {like_btn.innerHTML = `❤ ${event.target.innerHTML.slice(2)}`;};
    } else {
        like_btn.onmouseover = (event) => {event.target.innerHTML = `❤ ${event.target.innerHTML.slice(2)}`;};
        like_btn.onmouseleave = (event) => {like_btn.innerHTML = `\u2661 ${event.target.innerHTML.slice(2)}`;};
    }
    like_btn.onclick = event => like(event);
}