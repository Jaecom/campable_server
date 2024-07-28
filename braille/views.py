from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .algorithm.braille_algorithm import convert_file_to_braille
import pypandoc


@csrf_exempt
def index(request):
    if request.method == "POST":
        if "file" not in request.FILES:
            return HttpResponseBadRequest("Missing file")

        uploaded_file = request.FILES["file"]
        try:
            file_content = uploaded_file.read()

            output = pypandoc.convert_text(file_content, "latex", format="docx")

            result = convert_file_to_braille(output)

            response = HttpResponse(result, content_type="text/plain")
            response["Content-Disposition"] = (
                'attachment; filename="converted_file.txt"'
            )

            return response
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
