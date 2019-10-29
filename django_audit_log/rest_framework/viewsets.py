from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class AuditLogReadOnlyViewSet(ReadOnlyModelViewSet):

    audit_log_list_response = False

    def _get_filter_kwargs(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        return {self.lookup_field: self.kwargs.get(lookup_url_kwarg, "")}

    def _get_model_name(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return queryset.model.__name__

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        model = self._get_model_name()
        request.audit_log \
            .set_filter(object_name=model, kwargs=self._get_filter_kwargs()) \
            .set_results(response.data) \
            .info(f"Retrieve {model}")

        return response

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        model = self._get_model_name()
        search_terms = []
        for backend in list(self.filter_backends):
            if type(backend) == type(SearchFilter):
                search_terms += backend().get_search_terms(request)

        filter_kwargs = {str(getattr(self, 'search_fields', '')): search_terms}

        request.audit_log \
            .set_filter(object_name=model, kwargs=filter_kwargs) \
            .info(f"List {model}")

        if self.audit_log_list_response:
            request.audit_log.set_results(response.data)

        return response


class AuditLogViewSet(AuditLogReadOnlyViewSet, ModelViewSet):

    audit_log_list_response = False

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        model = self._get_model_name()
        request.audit_log \
            .set_results(response.data) \
            .info(f"Created {model} object")

        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        response = super().update(request, *args, **kwargs)

        model = self._get_model_name()
        message = f"Partial update of {model}" if partial else f"Update of {model}"
        request.audit_log \
            .set_filter(object_name=model, kwargs=self._get_filter_kwargs()) \
            .set_results(response.data) \
            .info(message)

        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)

        model = self._get_model_name()
        request.audit_log \
            .set_filter(object_name=model, kwargs=self._get_filter_kwargs()) \
            .set_results(response.data) \
            .info(f"Destroy {model}")

        return response

