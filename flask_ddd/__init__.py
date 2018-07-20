import importlib
import os


class DDD:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app_path = app.root_path
        app_package = app_path.split('/')[-1]
        contexts = list(
            dir for dir in os.listdir(app_path)
            if os.path.isdir(os.path.join(app_path, dir)))

        for context in contexts:
            context_package = f'{app_package}.{context}'
            try:
                registry_module = importlib.import_module(
                    '.domain.registries', package=context_package)
            except ImportError:
                continue
            try:
                repo_module = importlib.import_module(
                    '.adapter.repositories', package=context_package)
            except ImportError:
                pass
            else:
                registry_repo = getattr(registry_module, 'repos', None)
                if registry_repo:
                    repo_cls_names = getattr(repo_module, '__all__', ())
                    for repo_cls_name in repo_cls_names:
                        repo_cls = getattr(repo_module, repo_cls_name)
                        repo = repo_cls()
                        registry_name = getattr(repo, '__registry_name__')
                        setattr(registry_repo, registry_name, repo)

            try:
                service_module = importlib.import_module(
                    '.adapter.services', package=context_package)
            except ImportError:
                pass
            else:
                registry_service = getattr(registry_module, 'services', None)
                if registry_service:
                    service_names = getattr(service_module, '__all__', ())
                    for service_name in service_names:
                        service = getattr(service_module, service_name)
                        setattr(registry_service, service_name, service)
