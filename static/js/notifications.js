// 通知系统的JavaScript功能

// 定期检查新通知
function checkNotifications() {
    // 发送AJAX请求获取未读通知数量
    fetch('/notification/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notification-badge');
            if (badge) {
                // 更新通知徽章
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.textContent = '';
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('获取通知失败:', error));
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 立即检查一次通知
    checkNotifications();
    
    // 设置定时器，每60秒检查一次新通知
    setInterval(checkNotifications, 60000);
    
    // 为通知标记已读按钮添加AJAX功能
    document.querySelectorAll('.mark-read-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 更新UI，例如移除未读样式或隐藏按钮
                    const notificationItem = this.closest('.notification-item');
                    if (notificationItem) {
                        notificationItem.classList.remove('bg-light');
                        this.style.display = 'none';
                    }
                    // 重新检查通知数量
                    checkNotifications();
                }
            })
            .catch(error => console.error('标记已读失败:', error));
        });
    });
    
    // 为全部标为已读按钮添加AJAX功能
    const markAllReadBtn = document.querySelector('.mark-all-read-btn');
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('href');
            
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 更新UI，移除所有未读样式
                    document.querySelectorAll('.notification-item.bg-light').forEach(item => {
                        item.classList.remove('bg-light');
                    });
                    document.querySelectorAll('.mark-read-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                    // 重新检查通知数量
                    checkNotifications();
                }
            })
            .catch(error => console.error('全部标为已读失败:', error));
        });
    }
});