document.addEventListener('DOMContentLoaded', function() {
    const follow_btn = document.querySelector('#follow-btn')
    if (follow_btn !== null) {
        follow_btn.onclick = event => follow(event);
    }
    document.querySelectorAll('#edit-btn').forEach(btn => {
        btn.onclick = event => edit(event);
    })
    document.querySelectorAll('.like-btn').forEach(like_btn => {
        listen_likes(like_btn);
    })
});

function follow(event) {
    fetch('/follow', {
        method: "POST",
        body: JSON.stringify({
            type: event.target.dataset.type,
            user_id: event.target.dataset.user_id
        }),
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value
        }
    })
    .then(response => response.json())
    .then(result => {
        alert(result.message);
        document.querySelector('h5').innerHTML = `${result.follower_count} followers`;
        btn = document.querySelector('#follow-btn');
        btn.dataset.type = result.new_type;
        btn.innerHTML = result.new_type[0].toUpperCase() + result.new_type.slice(1);
    });
}