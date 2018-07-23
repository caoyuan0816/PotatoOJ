from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from potato import views


urlpatterns = [
    url(r'^whoami/$', views.whoami),
    url(r'^login/$', views.api_login),
    url(r'^logout/$', views.api_logout),
    url(r'^register/$', views.api_register),
    url(r'^question/$', views.api_questions),
    url(r'^question/(?P<pid>[0-9]{1,6})/$', views.api_question_details),
    url(r'^submit/$', views.api_submit),
    url(r'^status/$', views.api_statuses),
    url(r'^contests/$', views.api_contests),
    url(r'^contest/(?P<cid>[0-9]{1,6})/$', views.api_contest_details),
    url(r'^user/(?P<uid>[0-9]{1,6})/$', views.api_user_details),
    url(r'^group/$', views.APIGroupList.as_view()),
    url(r'^group/(?P<group_id>[0-9]+)/$', views.APIGroupDetail.as_view()),
    url(r'^group/(?P<group_id>[0-9]+)/user/$', views.APIGroupUserList.as_view()),
    url(r'^group/(?P<group_id>[0-9]+)/user/(?P<user_id>[0-9]+)/$', views.APIGroupUserDetail.as_view()),
    url(r'^test/(?P<contest_id>[0-9]+)/$', views.api_test_permission),
    url(r'^test/assign/$', views.api_test_assign_permission),
    url(r'^status/(?P<sid>[0-9]{1,8})/$', views.api_status_details),
    url(r'^question/status/(?P<pid>[0-9]{1,6})/$', views.api_problem_status),
    url(r'^contest/ranklist/(?P<cid>[0-9]{1,6})/$', views.api_contest_rank_list),
    url(r'^contest/statuslist/(?P<cid>[0-9]{1,6})/$', views.api_contest_status_list),
    url(r'^contest/(?P<cid>[0-9]{1,6})/status/(?P<sid>[0-9]{1,8})/$', views.api_contest_status_details)
]

urlpatterns = format_suffix_patterns(urlpatterns)
