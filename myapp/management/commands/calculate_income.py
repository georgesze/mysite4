from django.core.management.base import BaseCommand, CommandError
from myapp.models import AliOrd

class Command (BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('ord_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for ord_id in options['ord_id']:
            try:
                order = AliOrd.objects.get(OrderId=ord_id)
                #order = AliOrd.objects.all()
            except AliOrd.DoesNotExist:
                raise CommandError('Order "%s" does not exist' % ord_id)

                # order.opened = False
                # order.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % ord_id))

