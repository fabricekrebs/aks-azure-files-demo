import os
import logging
import mimetypes
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class FileListCreateAPIView(APIView):
    """API view for listing files and creating new files"""
    
    def get(self, request):
        """List all files in the storage directory"""
        try:
            files_path = settings.FILES_STORAGE_PATH
            
            # Ensure the directory exists
            if not os.path.exists(files_path):
                os.makedirs(files_path, exist_ok=True)
                return Response({'files': []})
            
            files = []
            for filename in os.listdir(files_path):
                file_path = os.path.join(files_path, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'mime_type': mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                    })
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            return Response({'files': files})
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return Response(
                {'error': f'Failed to list files: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new file"""
        try:
            filename = request.data.get('filename')
            content = request.data.get('content', '')
            
            if not filename:
                return Response(
                    {'error': 'Filename is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Sanitize filename to prevent directory traversal
            filename = os.path.basename(filename)
            
            if not filename or filename.startswith('.'):
                return Response(
                    {'error': 'Invalid filename'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            files_path = settings.FILES_STORAGE_PATH
            os.makedirs(files_path, exist_ok=True)
            
            file_path = os.path.join(files_path, filename)
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {filename}")
            
            return Response({
                'message': f'File "{filename}" created successfully',
                'filename': filename
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            return Response(
                {'error': f'Failed to create file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDetailAPIView(APIView):
    """API view for individual file operations"""
    
    def get(self, request, filename):
        """Get file content"""
        try:
            # Sanitize filename
            filename = os.path.basename(filename)
            files_path = settings.FILES_STORAGE_PATH
            file_path = os.path.join(files_path, filename)
            
            if not os.path.exists(file_path):
                return Response(
                    {'error': f'File "{filename}" not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return Response({
                'filename': filename,
                'content': content
            })
            
        except UnicodeDecodeError:
            return Response(
                {'error': 'File contains binary data and cannot be displayed as text'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            return Response(
                {'error': f'Failed to read file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, filename):
        """Delete a file"""
        try:
            # Sanitize filename
            filename = os.path.basename(filename)
            files_path = settings.FILES_STORAGE_PATH
            file_path = os.path.join(files_path, filename)
            
            if not os.path.exists(file_path):
                return Response(
                    {'error': f'File "{filename}" not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            os.remove(file_path)
            logger.info(f"Deleted file: {filename}")
            
            return Response({
                'message': f'File "{filename}" deleted successfully'
            })
            
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {str(e)}")
            return Response(
                {'error': f'Failed to delete file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    try:
        files_path = settings.FILES_STORAGE_PATH
        
        # Check if storage directory is accessible
        if os.path.exists(files_path):
            # Try to write a test file
            test_file = os.path.join(files_path, '.health_check')
            with open(test_file, 'w') as f:
                f.write('health_check')
            os.remove(test_file)
            storage_status = 'accessible'
        else:
            storage_status = 'directory_not_found'
        
        return Response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'storage_path': files_path,
            'storage_status': storage_status,
            'pod_name': os.environ.get('POD_NAME', 'unknown'),
            'node_name': os.environ.get('NODE_NAME', 'unknown'),
        })
        
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
