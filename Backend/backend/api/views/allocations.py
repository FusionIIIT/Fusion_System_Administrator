import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes

from ..permissions import Privileged
from ..services import allocations as service
from ..services.allocations import ServiceError

logger = logging.getLogger(__name__)


def _run(fn, *args):
    try:
        return JsonResponse(fn(*args))
    except ServiceError as exc:
        return JsonResponse(exc.payload, status=exc.status)
    except Exception:
        logger.exception("Unhandled error in allocation service")
        return JsonResponse({"success": False, "message": "An unexpected error occurred."}, status=500)


@api_view(["GET"])
def allocation_summary(request):
    return _run(service.summarize, request.GET.get("batch"), request.GET.get("semester"),
                request.GET.get("programme"))


@api_view(["POST"])
@permission_classes(Privileged)
def delete_allocation(request):
    return _run(service.delete_allocation, request.data.get("batch"),
                request.data.get("semester"), request.data.get("programme"),
                getattr(request.user, "username", ""))
