
For the Python only implementation (which is used by this library) see https://github.com/Amsterdam/python-audit-log


# DataPunt Django Audit Log

DataPunt Audit Log is a simple Django app that will log all incoming requests
and their corresponding responses to a configurable endpoint. 

During the process request phase, the logger is attached to the request. Before 
returning a response the app can easily provide extra context. In the process
response phase the audit_log middleware will send the log. 


## Links
- [Quick Start](#quick-start)
- [Default Context Info](#default-context-info)
- [Custom Optional Context Info](#custom-optional-context-info)
- [Django Rest Framework](#django-rest-framework)


## Quick start

1. Install using pip

    ```bash
    pip install datapunt_django_audit_log
    ```
   
2. Add "django_audit_log" to your INSTALLED_APPS:

    ```python
    INSTALLED_APPS = [
        ...
        'django_audit_log',
    ]
    ```

3. Add the AuditLogMiddleware to your MIDDLEWARE:

    ```python
    MIDDLEWARE = [
        ...
       'django_audit_log.middleware.AuditLogMiddleware',
    ]
    ```
   
4. When using the Django Rest Framework, let your viewsets extend `AuditLogReadOnlyViewset`
or `AuditLogViewSet`. This will automatically add context to the audit log regarding
filters, results and executed actions (see - [Django Rest Framework](#django-rest-framework)).

    ```python
    class MyViewSet(AuditLogViewSet):
        queryset = SomeModel.objects.all()
    ```

5. Set the AUDIT_LOG_EXEMPT_URLS setting to make sure certain urls will not be logged 
(e.g. health check urls). 

    ```python
    # If a URL path matches a regular expression in this list, the request will not be redirected to HTTPS.
    # The AuditLogMiddleware strips leading slashes from URL paths, so patterns shouldn’t include them, e.g.
    # [r'foo/bar$']
    AUDIT_LOG_EXEMPT_URLS = []
    ```


At this point all requests/responses will be logged. For providing extra context
(which you are strongly urged to do so), see next chapters.

## Default context info

By default the audit log sends the following json structure per request:

```json
{
  "http_request": {
    "method": "get|post|head|options|etc..",
    "url": "https://datapunt.amsterdam.nl?including=querystring",
    "user_agent": "full browser user agent"
  },
  "http_response": {
    "status_code": "http status code",
    "reason": "http status reason",
    "headers": {
      "key": "value"
    }
  },
  "user": {
    "authenticated": "True/False",
    "provider": "auth backend the user authenticated with",
    "realm": "optional realm when using keycloak or another provider",
    "email": "email of logged in user",
    "roles": "roles attached to the logged in user",
    "ip": "ip address"
  }
}
```
    
Each json entry is set by its corresponding method. In this case, 
the middleware sets them automatically by calling
`set_http_request()` and `set_user_fom_request()` 
in the process_request method. In the process_response method the
last data is set by invoking `set_http_response()`.

After the response has been processed the middleware automatically
creates the log item by calling `send_log()`. 
    
## Custom optional context info

Per request it is possible to add optional context info. For a complete
audit log, you are strongly urged to add more info inside your view.

Adding extra context is quite simple. The audit_log object has been added
to the request by the middleware. Therefore every view can simply access 
it via the request object.

### Filter 
`request.audit_log.set_filter(self, object_name, fields, terms)` allows to provide
info on the requested type of object and the filters that have been used 
(a user searches for 'terms', which are matched on specific 'fields' of the 
'object').

This method will add the following details to the log:

```json
"filter": {
      "object": "Object name that is requested",
      "fields": "Fields that are being filtered on, if applicable",
      "terms": "Search terms, if applicable"
  }
```

### Results
`request.audit_log.set_results(self, results)` allows to pass a json dict
detailing exactly what results have been returned to the user. 

It is up to the developer to decide whether the amount of 
data that would be added here will become a burden instead
of a blessing.

This method will add the following details to the log:

```json
"results": {
    ...
  }
```

### Message and loglevel
At last, a log message and loglevel can be provided to indicate 
what the request is actually doing. This is done by calling 
one of the following methods:

```python
request.audit_log.debug(self, msg)
request.audit_log.info(self, msg)
request.audit_log.warning(self, msg)
request.audit_log.error(self, msg)
request.audit_log.critical(self, msg)
```
    
These methods will add the following details to the log:

```json
"type": "DEBUG|INFO|WARNING|ERROR|etc",
"message": "log message"
```

## Django Rest Framework
Two base-ViewSets are available if you use the Django Rest Framework.

The `AuditLogReadOnlyViewSet` extends the `ReadOnlyModelViewSet` and overrides
the `retrieve()` and `list()` methods. The `AuditLogViewSet` extends the `AuditLogReadOnlyViewSet`
and overrides the remaining (non-read-only) methods `create()`, `update()` and `destroy()`.

Our classes inspect the request and will automatically add extra context information
to the audit log. This context information provides info regarding filters, results
and the action that is being performed.

Note that by default `list()` will not add the results to the log, unless the `audit_log_list_response`
attribute is set. Only do so when the amount of data inside the list response is suitable
to store inside a log entry.

```python
class MyViewSet(AuditLogViewSet):
    audit_log_list_response = True
```
