from livereload import Server, shell

if __name__ == '__main__':
    server = Server()
    server.watch('*.rst', shell('make html'), delay=2)
    server.watch('*.py', shell('make html'), delay=2)
    server.watch('_static/*', shell('make html'), delay=2)
    server.watch('_templates/*', shell('make html'), delay=2)
    server.serve(root='_build/html', port=5500)
