from django.urls import path, include
from rest_framework.routers import DefaultRouter
from battle.views import views, users, clubs, games, gameMembers, playgrounds, clubAccount

router = DefaultRouter(trailing_slash=False)
router.register(r'users', users.UsersViewSet)
router.register(r'clubs', clubs.ClubsViewSet)
router.register(r'members', views.MembersViewSet)
router.register(r'apply', views.ApplyViewSet)
router.register(r'playgrounds', playgrounds.PlaygroundsViewSet)
router.register(r'games', games.GamesViewSet)
router.register(r'game-members', gameMembers.GameMembersViewSet)
router.register(r'upload', views.ImageUploadViewSet)
router.register(r'club-account', clubAccount.ClubAccountViewSet)
router.register(r'club-account-record', clubAccount.ClubAccountViewSet)
# router.register(r'relatives', views.RelativesViewSet)
# router.register(r'advert', views.AdvertViewSet)
# router.register(r'arts', views.ArtsViewSet)
# router.register(r'message', views.MessageViewSet)
# 管理后台
# router.register(r'admin.users', views_admin.AdminUsersViewSet)
# router.register(r'admin.family', views_admin.AdminFamilyViewSet)
# router.register(r'admin.ranks', views_admin.AdminRanksViewSet)
# router.register(r'admin.members', views_admin.AdminMembersViewSet)
# router.register(r'admin.apply', views_admin.AdminApplyViewSet)
# router.register(r'admin.codes', views_admin.AdminCodesViewSet)
# router.register(r'admin.felatives', views_admin.AdminRelativesViewSet)
# router.register(r'admin.advert', views_admin.AdminAdvertViewSet)
# router.register(r'admin.arts', views_admin.AdminArtsViewSet)
# router.register(r'admin.upload', views_admin.ImageUploadViewSet)
# router.register(r'admin.message', views_admin.AdminMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
