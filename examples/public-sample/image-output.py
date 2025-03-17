'''
[Image output example]

$ ipserver --port=8001 --http_app=./examples/ipserver-sample/
URL: http://your-host:8001/image-output
'''

try:
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
    import io

    def generate_art(image_size=(400, 400), num_shapes=50):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, image_size[0])
        ax.set_ylim(0, image_size[1])
        ax.axis('off')

        gradient = np.linspace(0, 1, image_size[1])
        gradient = np.vstack((gradient, gradient)).T
        cmap = LinearSegmentedColormap.from_list('gradient', ['#5588f0', '#ebcd87'])
        ax.imshow(gradient, aspect='auto', cmap=cmap, extent=[0, image_size[0], 0, image_size[1]], zorder=-1)

        fig.patch.set_facecolor('lightblue')
        ax.set_facecolor('lightblue')

        colors = ['#33c7dF', '#3357d8', '#3357FF', '#e1cc33']
        shapes = ['circle', 'rectangle', 'polygon']

        for i in range(num_shapes):
            shape_type = shapes[i % len(shapes)]
            color = colors[i % len(colors)]
            x, y = np.random.uniform(0, image_size[0]), np.random.uniform(0, image_size[1])
            if shape_type == 'circle':
                radius = np.random.uniform(50, 200)
                circle = plt.Circle((x, y), radius, color=color, alpha=0.2)
                ax.add_patch(circle)
            elif shape_type == 'rectangle':
                width, height = np.random.uniform(100, 300), np.random.uniform(100, 300)
                rectangle = plt.Rectangle((x - width / 2, y - height / 2), width, height, color=color, alpha=0.2, angle=np.random.uniform(0, 360))
                ax.add_patch(rectangle)
            elif shape_type == 'polygon':
                num_vertices = np.random.choice([3, 4, 5, 6])
                angles = np.linspace(0, 2 * np.pi, num_vertices, endpoint=False)
                radius = np.random.uniform(50, 200)
                points = np.stack((np.cos(angles), np.sin(angles)), axis=1) * radius + [x, y]
                polygon = plt.Polygon(points, color=color, alpha=0.1)
                ax.add_patch(polygon)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        plt.close(fig)

        return buf.getvalue()

    buf = generate_art()

    httpio.content_type = 'image/png'
    httpio.print_byte(buf)
except Exception:
    httpio.print('<html>Require: matplotlib.pyplot, numpy</html>')
