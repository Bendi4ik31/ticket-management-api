from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import notify_ticket_status_change, process_critical_alert
from rest_framework.permissions import IsAdminUser

from .models import Ticket
from .serializers import TicketSerializer
class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer
    search_fields = ['title', 'description']
    def get_queryset(self):
            if self.request.user.is_staff:
                  return Ticket.objects.all()
            return Ticket.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
          ticket = serializer.save(author=self.request.user)
          if ticket.priority == Ticket.Priority.CRITICAL:
                        process_critical_alert.delay(ticket.id)

    @action(methods=['post'],detail=True,permission_classes=[IsAdminUser])
    def take(self,request,pk=None):
            permission_classes=[IsAdminUser]
            ticket  = self.get_object()
            if ticket.status in [Ticket.Status.RESOLVED < Ticket.Status.CLOSED]:
                return Response(
                      {
                            'detail':'чувак завершений тикет не можна взяти на роботу'
                      },status=status.HTTP_400_BAD_REQUEST
                )
            ticket.assigned_to = request.user
            ticket.status = Ticket.Status.IN_PROGRESS
            ticket.save()
            notify_ticket_status_change.delay(ticket.id, ticket.status)
            return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)
    @action(methods=['post'], detail=True)
    def resolve(self, request, pk=None):
        ticket = self.get_object()

        if ticket.status != Ticket.Status.IN_PROGRESS:
            return Response(
                {"detail": "Спочатку візьміть тикет у роботу!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket.status = Ticket.Status.RESOLVED
        ticket.save()
        notify_ticket_status_change.delay(ticket.id, ticket.status)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)