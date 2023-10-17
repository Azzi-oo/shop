# import redis
from django.conf import settings
from .models import Product

# r = redis.Redis(host=settings.REDIS_HOST,
#                 port=settings.REDIS_PORT,
#                 db=settings.REDIS_DB)


class Recommender:
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'
    
    def products_bought(self, products):
        products_ids = [p.id for p in products]
        for product_id in products_ids:
            for with_id in products_ids:
                # получить другие товары, купленные с каждым товаром
                if product_id != with_id:
                    # увеличить балл товара, купленного вместе
                    r.zincrby(self.get_product_key(product_id),
                              1,
                              with_id)
                    
    def suggest_products_for(self, products, max_results=6):
        products_ids = [p.id for p in products]
        if len(products) == 1:
            # only 1 
            suggestions = r.zrange(
                        self.get_product_key(product_ids[0]),
                        0, -1, desc=True)[:max_results]
        else:
            # generate timely keys
            flat_ids = ''.join([str(id) for id in products_ids])
            tmp_key = f'tmp_{flat_ids}'
            # несколько товаров, обьеденить баллы всех товаров
            # сохранить полеченное сортированное множество
            keys = [self.get_product_key(id) for id in products_ids]
            r.zunionstore(tmp_key, keys)
            # delete id
            r.zrem(tmp_key, *products_ids)
            # get id for count
            suggestions = r.zrange(tmp_key, 0, -1,
                                   desc=True)[:max_results]
            # delete key
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        # get recommended and sort
        suggested_products = list(Product.objects.filter(
            id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products
            
