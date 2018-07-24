from .domain.registries import repos


def articles_by_page(page=0, page_count=10):
    articles = repos.article.recent_articles_of_page(page, page_count)
    return articles


def article_by_id(id):
    article = repos.article.article(id)
    return article