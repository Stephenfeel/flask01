var currentCid = 0; // 当前分类 id
var cur_page = 0; // 当前页
var orgin_page=0;//原始页
var is_get=true;
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    //初始化vue对象
     vue_list_con=new Vue({
         el:'.list_con',
         delimiters:['[[',']]'],
         data:{
             news_list:[],
         },
     });
    updateNewsData();


    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // TODO 去加载新闻数据
            currentCid=clickCid;
            cur_page=0;
            updateNewsData(currentCid);

        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100&&is_get) {
            // TODO 判断页数，去更新新闻数据
            if(cur_page<=total_page){
                updateNewsData()
            }
        }
    })


})

function updateNewsData() {
    // TODO 更新新闻数据
    //进行判断:当前也得数据如果未加载到，则不再发请求
    is_get=false
    $.get('/newslist',{
        'page':cur_page+1,
        'category_id':currentCid
    },function (data) {
        if(cur_page==0){
            vue_list_con.news_list=data.news_list2
        }
        else {
           vue_list_con.news_list=data.news_list2.concat(vue_list_con.news_list)
        }
        vue_list_con.news_list=data.news_list2.concat(vue_list_con.news_list)
        total_page=data.total_page;
        //接受并保存当前页码
         cur_page=data.page;
        is_get=true;
    })


    //方法不太好
    // if(orgin_page!=cur_page){
    //     return
    // }
    // $.get('/newslist',{
    //     'page':cur_page+1
    // },function (data) {
    //     vue_list_con.news_list=data.news_list2.concat(vue_list_con.news_list)
    //     //接受并保存当前页码
    //     cur_page=data.page;
    // });
    // orgin_page=cur_page+1
}
