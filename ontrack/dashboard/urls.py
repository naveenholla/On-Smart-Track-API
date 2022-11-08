from django.urls import path

from .views import index_dashboard_view

app_name = "dashboard"
urlpatterns = [
    path("index", view=index_dashboard_view, name="index"),
    path("analytics", view=index_dashboard_view, name="analytics"),
    path("projects", view=index_dashboard_view, name="projects"),
    path("wallet", view=index_dashboard_view, name="wallet"),
    path("widgets", view=index_dashboard_view, name="widgets"),
    # demo
    path("demo-saas-dark", view=index_dashboard_view, name="demo.saas-dark"),
    path("demo-saas-rtl", view=index_dashboard_view, name="demo.saas-rtl"),
    path(
        "demo-horizontal-creative",
        view=index_dashboard_view,
        name="demo.horizontal-creative",
    ),
    path(
        "demo-horizontal-creative-dark",
        view=index_dashboard_view,
        name="demo.horizontal-creative-dark",
    ),
    path(
        "demo-horizontal-creative-rtl",
        view=index_dashboard_view,
        name="demo.horizontal-creative-rtl",
    ),
    path(
        "demo-detached-modern", view=index_dashboard_view, name="demo.detached-modern"
    ),
    path(
        "demo-detached-modern-dark",
        view=index_dashboard_view,
        name="demo.detached-modern-dark",
    ),
    path(
        "demo-detached-modern-rtl",
        view=index_dashboard_view,
        name="demo.detached-modern-rtl",
    ),
    path(
        "demo-index-light-sidenav-layout",
        view=index_dashboard_view,
        name="demo.index-light-sidenav-layout",
    ),
    path(
        "demo-index-semi-dark-layout",
        view=index_dashboard_view,
        name="demo.index-semi-dark-layout",
    ),
    path(
        "demo-horizontal-boxed", view=index_dashboard_view, name="demo.horizontal-boxed"
    ),
    path("demo-full-dark", view=index_dashboard_view, name="demo.full-dark"),
    path("demo-full-rtl", view=index_dashboard_view, name="demo.full-rtl"),
]
