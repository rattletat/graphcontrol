from django.apps import apps

from graphwatch.core.models import Group


class TwitterGroup(Group):
    pass


class AccountGroup(TwitterGroup):
    def get_nodes_queryset(self):
        Account = apps.get_model("twitter.Account")
        return Account.objects.all()

    # def __str__(self, n=3):
    #     n_names = map(str, self.nodes.order_by("?")[:n])
    #     text = f'{self.name}: {", ".join(n_names)}'
    #     if (count := self.nodes.count()) > n:
    #         text += f" and {count-n} more."
    #     return text
