```c
void bubble_sort(int *arr, int n)
{
  int newn;
  do {
    newn = 0;
    for (int i = 1; i < n; i++) {
      if (arr[i - 1] > arr[i]) {
        int tmp = arr[i - 1];
        arr[i - 1] = arr[i];
        arr[i] = tmp;
        newn = i;
      }
    }
    n = newn;
  } while (newn > 0);
}
```