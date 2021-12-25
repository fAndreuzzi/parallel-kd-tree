#include "tree_mpi.h"
#include <mpi.h>

#include <iostream>
#include <limits>

#define SIZE 6
#define DIMS 2

void print(KNode *tree, int depth);

int main(int argc, char **argv) {
  MPI_Init(&argc, &argv);

  int rank;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  data_type *dt = nullptr;
  if (rank == 0) {
    dt = new data_type[SIZE * DIMS];

    for (int i = 0; i < SIZE; i++) {
      dt[i * 2] = 9 - i;
      dt[i * 2 + 1] = 1 + i;
    }

    for (int i = 0; i < SIZE * DIMS; i++) {
#ifdef DEBUG
      std::cout << i << " -> " << dt[i] << std::endl;
#endif
    }
  }

  int size = SIZE;

  double start_time = MPI_Wtime();
  KNode *tree = generate_kd_tree(dt, size, DIMS);
  double end_time = MPI_Wtime();

  // we can now delete the data safely
  delete[] dt;

#ifdef DEBUG
  if (rank == 0) {
    print(tree, 0);
  }
#endif

  delete tree;

#ifdef TIME
  if (rank == 0) {
    std::cout << "# " << end_time - start_time << std::endl;
  }
#endif

  MPI_Finalize();
}

void print_node(KNode *node) {
  std::cout << "(";
  for (int i = 0; i < dims; i++) {
    if (i > 0)
      std::cout << ",";
    if (node->get_data(i) == std::numeric_limits<int>::min()) {
      std::cout << "n/a";
      break;
    } else
      std::cout << node->get_data(i);
  }
  std::cout << ")";
}

void print(KNode *tree, int depth) {
  std::cout << "depth = " << depth << std::endl;

  print_node(tree);
  std::cout << std::endl;

  if (tree->get_left()) {
    std::cout << "left node of ";
    print_node(tree);
    std::cout << " -- ";

    print(tree->get_left(), depth + 1);
  }
  if (tree->get_right()) {
    std::cout << "right node of ";
    print_node(tree);
    std::cout << " -- ";

    print(tree->get_right(), depth + 1);
  }
}
