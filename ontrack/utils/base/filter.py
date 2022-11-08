# class MyFilterView(FilterByAttrsMixin, django_filters.views.FilterView):
#     ...
#     filterset_class = MyFiltersetClass

# class MyFiltersetClass(django_filters.FilterSet):
#     is_static = django_filters.BooleanFilter(
#         method='attr_filter_is_static',
#     )

#     class Meta:
#         model = MyModel
#         fields = [...]

#     @attr_filter
#     def attr_filter_is_static(self, queryset, name, value):
#         return [instance for instance in queryset if instance.is_static]

# class FilterByAttrsMixin:

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         filtered_list = self.filter_qs_by_attributes(self.object_list, self.filterset)
#         context.update({
#             'object_list': filtered_list,
#         })
#         return context

#     def filter_qs_by_attributes(self, queryset, filterset_instance):
#         if hasattr(filterset_instance.form, 'cleaned_data'):
#             for field_name in filter_instance.filters:
#                 method_name = f'attr_filter_{field_name}'
#                 if hasattr(filterset_instance, method_name):
#                     value = filterset_instance.form.cleaned_data[field_name]
#                     if value:
#                         queryset = getattr(filterset_instance,
#                               filter_method_name)(queryset, field_name, value, force=True)
#         return queryset

# def attr_filter(func):

#     def wrapper(self, queryset, name, value, force=False, *args, **kwargs):
#         if force:
#             return func(self, queryset, name, value, *args, **kwargs)
#         else:
#             return queryset
#     return wrapper
