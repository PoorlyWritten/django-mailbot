from tastypie.resources import ModelResource
from introductions.models import Introduction


class IntroductionResource(ModelResource):
    class Meta:
        queryset = Introduction.objects.all()

    def get_object_list(self, request):
        return super(IntroductionResource, self).get_object_list(request).filter(connector=request.user)
