from app import app, scheduler
from .itemOrdering import findItemOrdering
from .itemSuggestions import findItemSuggestions
from .clusterShoppings import clusterShoppings


@app.before_first_request
def load_jobs():
    # for debugging:
    # @scheduler.task('interval', id='test', seconds=5)
    # def test():
    #     print("--- test analysis is starting ---")
    #     shopping_instances = clusterShoppings()
    #     findItemOrdering(shopping_instances)
    #     findItemSuggestions(shopping_instances)
    #     print("--- test analysis is completed ---")

    @scheduler.task('cron', id='everyDay', day_of_week='*', hour='3')
    def daily():
        print("--- daily analysis is starting ---")
        shopping_instances = clusterShoppings()
        findItemOrdering(shopping_instances)
        findItemSuggestions(shopping_instances)
        print("--- daily analysis is completed ---")
