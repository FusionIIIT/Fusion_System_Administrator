import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes

from ..permissions import Privileged
from ..services import batches as service
from ..services.batches import ServiceError

logger = logging.getLogger(__name__)


def _run(fn, *args):
    try:
        return JsonResponse(fn(*args))
    except ServiceError as exc:
        return JsonResponse(exc.payload, status=exc.status)
    except Exception:
        logger.exception("Unhandled error in batch service")
        return JsonResponse({"success": False, "message": "An unexpected error occurred."}, status=500)


@api_view(["GET"])
def list_disciplines(request):
    return _run(service.list_disciplines)


@api_view(["GET"])
def list_curriculums(request):
    return _run(service.list_curriculums)


@api_view(["GET"])
def sync_batch_data(request):
    return _run(service.sync_batches)


@api_view(["GET"])
def get_batch_students(request, batch_id):
    return _run(service.batch_students, batch_id, request.query_params.get("specialization"))


@api_view(["POST"])
@permission_classes(Privileged)
def create_batch(request):
    return _run(service.create_batch, request.data)


@api_view(["DELETE", "POST"])
@permission_classes(Privileged)
def delete_batch(request, batch_id):
    return _run(service.delete_batch, batch_id)


@api_view(["POST"])
@permission_classes(Privileged)
def save_students_batch(request):
    return _run(service.save_students, request.data)


@api_view(["POST"])
@permission_classes(Privileged)
def add_single_student(request):
    return _run(service.add_student, request.data)
