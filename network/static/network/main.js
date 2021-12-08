document.addEventListener('DOMContentLoaded', function() {
    const post_form = document.querySelector('#post-form');
    if (post_form !== null) {
        post_form.onsubmit = event => create_post(event);
    }
    populate_posts(1);
});


function create_post(event) {
    event.preventDefault();
    const content = document.querySelector('#new_content').value;
    fetch('/post', {
        method: 'POST',
        body: JSON.stringify({
            content: content
        }),
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
        }
    })
    .then(response => response.json())
    .then(result => {
        alert(result.message);
        populate_posts(1);
    });

}

function populate_posts(num) {
    const container = document.querySelector('#post-container');
    container.innerHTML = "";
    document.querySelector('#new_content').value = "";
    const count = num * 10;
    fetch(`/get_posts/${count}`)
    .then(response => response.json())
    .then(result => {
        result.posts.forEach(post => {
            const post_container = document.createElement('div');
            const author = document.createElement('a');
            const timestamp = document.createElement('div');
            const like = document.createElement('div');
            const content = document.createElement('div');

            let edit_btn = null;
            if (post.viewer_id === post.author_id) {
                edit_btn = document.createElement('button');
                edit_btn.classList.add('btn', 'btn-primary', 'btn-sm', 'mt-2');
                edit_btn.id = 'edit-btn';
                edit_btn.innerHTML = 'Edit';
                
            }
            
            author.innerHTML = post.author;
            timestamp.innerHTML = post.timestamp;
            if (post.liked) {
                like.innerHTML = `❤ ${post.like}<br>`;
                like.dataset.liked = 'true';
            } else {
                like.innerHTML = `\u2661 ${post.like}<br>`;
                like.dataset.liked = 'false';
            }
            like.classList.add('like-btn');
            listen_likes(like);
            content.innerText = post.content;
            content.classList.add('post-content')

            post_container.classList.add('border', 'border-dark', 'p-2', 'my-3');
            author.style.fontWeight = 'bold';
            author.classList.add('my-2');
            author.href = `profile/${post.author_id}`;
            author_container = document.createElement('div');
            author_container.append(author);
            timestamp.style.color = 'grey';

            post_container.append(author_container);
            post_container.append(content);
            post_container.append(timestamp);
            post_container.append(like);
            if (edit_btn !== null) {
                edit_btn.onclick = event => edit(event);
                post_container.append(edit_btn);
            }

            post_container.dataset.post_id = post.post_id
            container.append(post_container);
        });
    });
}
