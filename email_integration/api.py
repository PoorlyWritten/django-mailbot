from tastypie.resources import ModelResource
from .models import Introduction


class IntroductionResource(ModelResource):
    class Meta:
        queryset = Introduction.objects.all()
        always_return_data = True

    def get_object_list(self, request):
        return super(IntroductionResource, self).get_object_list(request).filter(connector=request.user)
