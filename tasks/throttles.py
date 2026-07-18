from rest_framework.throttling import UserRateThrottle


class CommentCreationThrottle(UserRateThrottle):
    scope = "comment_create"

    def allow_request(self, request, view):

        if request.method != "POST":
            return True
        return super().allow_request(request, view)
