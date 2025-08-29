import { Injectable, inject } from '@angular/core';
import {
  HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
// Si usas PrimeNG Toast:
import { MessageService } from 'primeng/api';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {
  private message = inject(MessageService, { optional: true });

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((err: HttpErrorResponse) => {
        const { summary, detail } = this.translateError(err);

        // Toast si está disponible, si no usa alert
        if (this.message) {
          this.message.add({ severity: 'error', summary, detail });
        } else {
          alert(`${summary}\n${detail}`);
        }
        // Re-lanzamos para que el componente pueda reaccionar si quiere
        return throwError(() => err);
      })
    );
  }

  private translateError(err: HttpErrorResponse): { summary: string; detail: string } {
    // Mensaje del backend (FastAPI) si viene
    const backendDetail =
      (err?.error && (err.error.detail || err.error.message)) ||
      null;

    // 1) Errores de red / CORS (con fetch suele ser status 0 o TypeError: Failed to fetch)
    if (err.status === 0) {
      const isFailedToFetch =
        (err?.message && /Failed to fetch/i.test(err.message)) ||
        (typeof err?.error === 'string' && /Failed to fetch/i.test(err.error));

      const detail = isFailedToFetch
        ? 'No se pudo contactar al servidor. Verifica tu conexión o que el servidor permita CORS.'
        : 'No se pudo completar la solicitud. Revisa tu conexión a internet o el servidor no está disponible.';

      return {
        summary: 'Error de conexión',
        detail,
      };
    }

    // 2) Mapeo por status
    switch (err.status) {
      case 400:
        return {
          summary: 'Solicitud inválida',
          detail: backendDetail || 'Revisa los datos enviados.',
        };

      case 401:
        return {
          summary: 'No autorizado',
          detail: backendDetail || 'Credenciales inválidas. Intenta nuevamente.',
        };

      case 403:
        return {
          summary: 'Acceso denegado',
          detail: backendDetail || 'No tienes permisos para realizar esta acción.',
        };

      case 404:
        return {
          summary: 'No encontrado',
          detail: backendDetail || 'El recurso solicitado no existe.',
        };

      case 409:
        return {
          summary: 'Conflicto',
          detail: backendDetail || 'La operación no puede completarse por un conflicto de datos.',
        };

      case 422:
        // FastAPI suele devolver detail como lista de errores de validación
        if (Array.isArray(err?.error?.detail)) {
          const msgs = err.error.detail
            .map((d: any) => {
              const loc = Array.isArray(d?.loc) ? d.loc.join('.') : d?.loc;
              return `• ${loc ?? 'campo'}: ${d?.msg ?? 'inválido'}`;
            })
            .join('\n');
          return {
            summary: 'Datos inválidos',
            detail: msgs || 'Algunos campos no son válidos.',
          };
        }
        return {
          summary: 'Datos inválidos',
          detail: backendDetail || 'Revisa los campos ingresados.',
        };

      case 429:
        return {
          summary: 'Demasiadas solicitudes',
          detail: backendDetail || 'Inténtalo de nuevo en unos momentos.',
        };

      default:
        if (err.status >= 500) {
          return {
            summary: 'Error del servidor',
            detail: backendDetail || 'Ocurrió un error inesperado. Inténtalo más tarde.',
          };
        }
        // Fallback genérico
        return {
          summary: `Error ${err.status}`,
          detail: backendDetail || err.statusText || 'Ocurrió un error inesperado.',
        };
    }
  }
}
