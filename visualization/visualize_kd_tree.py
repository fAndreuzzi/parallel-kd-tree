import numpy as np
import matplotlib.pyplot as plt
from collections import namedtuple

KDTreeNode = namedtuple("KDTreeNode", ["value", "left", "right"])

# make sure that the items of coord_matrix does not exceed upper/lower
# limits
def cut_matrix(m, lower_limit, upper_limit):
    m[m < lower_limit] = lower_limit
    m[m > upper_limit] = upper_limit


# find minimum and maximum values (overall, not vectorial) in the KDTree
def find_min_max(root):
    to_visit = [root]
    mn = 1e10
    mx = -1e10
    while to_visit:
        node = to_visit.pop()
        mn = min(*node.value, mn)
        mx = max(*node.value, mx)

        if node.left:
            to_visit.append(node.left)
        if node.right:
            to_visit.append(node.right)
    return mn, mx


# a convenient class which allows visualizing a KDTree along with some (small)
# configuration.
# - plane_alpha is the opacity of the surfaces drawn in the volume which
#   represents the tree;
# - intersection_lines_width is the width of the lines drawn on the surfaces
#   incident on the point which determined the split represented by the plane;
# - point_size is the dimension of the marker which represents split points in
#   the volume.
class KDTreeVisualization:
    def __init__(
        self, plane_alpha=0.4, intersection_lines_width=3, point_size=75
    ):
        self.plane_alpha = plane_alpha
        self.intersection_lines_width = intersection_lines_width
        self.point_size = point_size

        self.min_value = 0
        self.max_value = 0

    # generate an appropriate surface determined by a split in a point with
    # coordinate `values` along `axis`.
    def get_surface(self, values, axis):
        non_split_axes = np.meshgrid(
            *tuple(
                np.linspace(self.min_value, self.max_value, 10)
                for _ in range(self.n_axes - 1)
            )
        )
        data = [
            np.zeros_like(non_split_axes[0], dtype=float)
            for _ in range(self.n_axes)
        ]

        k = 0
        for i in range(self.n_axes):
            if i == axis:
                data[i] = np.full_like(non_split_axes[0], values[i])
            else:
                data[i] = non_split_axes[k]
                k += 1

        return tuple(data)

    # generate lines lying on the plane represented by tp_matrices (a tuple of
    # matrices containing the coordinates of the planes) generated by the point
    # whose coordinates are `values` after a split along `split_axis`
    def strong_lines(self, tp_matrices, values, split_axis):
        result = [[0 for _ in values] for _ in range(len(values) - 1)]

        # if we encountered the index corresponding to split_axis, we should subtract one to
        # i since result is one less item than tp_matrices
        subtract_one = False
        for i in range(len(tp_matrices)):
            if i != split_axis:
                # i-th coord is constant in the i-th line
                for j in range(len(values)):
                    i_temp = i - 1 if subtract_one else 0

                    if j == i:
                        result[i_temp][j] = (values[i], values[i])
                    elif j == split_axis:
                        result[i_temp][split_axis] = (
                            values[split_axis],
                            values[split_axis],
                        )
                    else:
                        result[i_temp][j] = (
                            np.min(tp_matrices[j]),
                            np.max(tp_matrices[j]),
                        )
            else:
                subtract_one = True
        return result

    # lower/upper_limit are the lower limit for this function call on all the
    # axes mn/mx are the min/max limit used in linspace to define an
    # experimental plane (to be cut according to limits)
    def draw_node(self, ax, node, lower_limits, upper_limits, depth):
        if node == None:
            return

        split_axis = depth % self.n_axes

        tp = self.get_surface(node.value, split_axis)
        for i in range(len(tp)):
            cut_matrix(tp[i], lower_limits[i], upper_limits[i])

        ax.plot_surface(*tp, alpha=self.plane_alpha)
        ax.scatter(*node.value, marker="o", s=self.point_size)

        lines = self.strong_lines(tp, node.value, split_axis)
        for l in lines:
            ax.plot(*l, color="k", linewidth=self.intersection_lines_width)

        left_lower_limits = list(lower_limits)
        left_upper_limits = list(upper_limits)
        left_upper_limits[split_axis] = node.value[split_axis]
        self.draw_node(
            ax, node.left, left_lower_limits, left_upper_limits, depth + 1
        )

        right_lower_limits = list(lower_limits)
        right_upper_limits = list(upper_limits)
        right_lower_limits[split_axis] = node.value[split_axis]
        self.draw_node(
            ax, node.right, right_lower_limits, right_upper_limits, depth + 1
        )

    # visualize the KDTree rooted in `root`. this method also computes some
    # instance variables (min_value, max_value, n_axes) used by other methods
    # of this class.
    def visualize(
        self,
        root,
        figsize=(20, 20),
        dpi=100,
        filename=None,
        camera_elevation=15,
        camera_rotation=30,
    ):
        fig = plt.figure(figsize=figsize, dpi=dpi)
        n_axes = len(root.value)

        self.min_value, self.max_value = find_min_max(root)
        self.n_axes = len(root.value)

        ax = fig.add_subplot(111, projection="3d")
        self.draw_node(ax, root, [-np.infty] * n_axes, [np.infty] * n_axes, 0)

        if filename:
            ax.view_init(elev=camera_elevation, azim=camera_rotation)
            fig.savefig(
                filename, dpi=fig.dpi, bbox_inches="tight", transparent=True
            )
        else:
            plt.show()