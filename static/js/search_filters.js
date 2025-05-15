// 处理搜索页面的筛选标签功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有筛选标签
    const filterBadges = document.querySelectorAll('.filter-badge i');
    
    // 为每个标签添加点击事件
    filterBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            // 获取当前URL和参数
            const currentUrl = new URL(window.location.href);
            const params = currentUrl.searchParams;
            
            // 获取要移除的筛选条件
            const filterToRemove = this.getAttribute('data-filter');
            
            // 根据筛选条件类型移除相应参数
            if (filterToRemove === 'price') {
                // 价格区间需要同时移除最低和最高价格
                params.delete('min_price');
                params.delete('max_price');
            } else {
                // 移除单个参数
                params.delete(filterToRemove);
            }
            
            // 更新URL并重新加载页面
            currentUrl.search = params.toString();
            window.location.href = currentUrl.toString();
        });
    });
    
    // 高亮显示当前排序方式
    const sortOptions = document.querySelectorAll('.sort-option');
    const currentSort = new URLSearchParams(window.location.search).get('sort_by') || 'newest';
    
    sortOptions.forEach(option => {
        if (option.getAttribute('data-sort') === currentSort) {
            option.classList.add('active');
        }
        
        // 添加排序选项点击事件
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const sortValue = this.getAttribute('data-sort');
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('sort_by', sortValue);
            window.location.href = currentUrl.toString();
        });
    });
});