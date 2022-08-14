function addComment(sachId){
    let content = document.getElementById('commentId')
    if (content !== null){
        fetch('/api/comments',{
            method: 'post',
            body: JSON.stringify({
                'sach_id': sachId,
                'content': content.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            console.info(data)
            if (data.status == 201){
                let comments = document.getElementById('commentArea')
                comments.innerHTML = getHtmlComment(data.comment) + comments.innerHTML
                content.value = ''
            }else{
                alert(data.err_msg)
            }
        }).catch(err => console.error(err))
    }
}

function getComments(sachId, page=1){
    fetch(`/api/sach/${sachId}/comments?page=${page}`).then(res => res.json()).then(data =>{
        console.info(data)
        let comments = document.getElementById('commentArea')
        comments.innerHTML = ''
        for(let i = 0; i < data.length; i++)
            comments.innerHTML += getHtmlComment(data[i])
    })
}

function getHtmlComment(comment){
    let image = comment.user.hinhanh
    if (image === null || !image.startsWith('https'))
        image = '/static/images/avatardefault.png'
    return `
        <div class="row">
              <div class="col-md-1 col-xs-4">
                <img src="/static/images/${comment.user.hinhanh}"
                     alt="${comment.user.username}" class="img-fluid rounded-circle" width="60px">
              </div>
              <div class="col-md-11 col-xs-8">
                <p><b>${comment.user.username}:</b> ${comment.content}</p>
                <p style="font-size:12px"><em>${moment(comment.created_date).locale('vi').fromNow()}</em></p>
              </div>
        </div>
    `
}

function addCart(id, name, price){
    event.preventDefault()

    fetch('/api/add-cart', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity
    }).catch(function(err) {
        console.error(err)
    })
}

function pay(){
    if(confirm('Bạn có chắc chắn thanh toán không ?') == true){
      fetch('/api/pay', {
            method: 'post'
        }).then(res => res.json()).then(data => {
            if (data.code == 200)
                location.reload()
        }).catch(err => console.error(err))
    }
}

function order(){
    if(confirm('Bạn có chắc chắn đặt hàng không ?') == true){
      fetch('/api/order', {
            method: 'post'
        }).then(res => res.json()).then(data => {
            if (data.code == 200)
                location.reload()
        }).catch(err => console.error(err))
    }
}

function updateCart(id, obj){
    fetch('/api/update-cart', {
            method: 'put',
            body: JSON.stringify({
                'id': id,
                'quantity': parseInt(obj.value)
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            let counter = document.getElementsByClassName('cart-counter')
            for (let i = 0; i < counter.length; i++)
                counter[i].innerText = data.total_quantity

            document.getElementById('total-amount').innerText = new Intl.NumberFormat().format(data.total_amount)
        }).catch(err => console.error(err))
}

function deleteCart(id){
    if(confirm('Bạn có chắc chắn xóa sản phẩm này không ?') == true){
      fetch('/api/delete-cart/' + id, {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            let counter = document.getElementsByClassName('cart-counter')
            for (let i = 0; i < counter.length; i++)
                counter[i].innerText = data.total_quantity

            document.getElementById('total-amount').innerText = new Intl.NumberFormat().format(data.total_amount)

            let e = document.getElementById('sach' + id)
            e.style.display = 'none'

        }).catch(err => console.error(err))
    }
}

