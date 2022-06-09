function deleteProduct(productId) {
  fetch("/delete-product", {
    method: "POST",
    body: JSON.stringify({ productId: productId }),
  }).then((_res) => {
    window.location.href = "/fridge";
  });
}

function useProduct(productId) {
  fetch("/use-product", {
    method: "POST",
    body: JSON.stringify({ productId: productId }),
  }).then((_res) => {
    window.location.href = "/fridge";
  });
}

function deleteListProduct(productId, listId) {
  fetch("/shopping-list/delete-product", {
    method: "POST",
    body: JSON.stringify({ productId: productId }),
  }).then((_res) => {
    window.location.href = "/shopping-lists/list/"+listId.toString();
  });
}

function deleteList(listId) {
  fetch("/delete-list", {
    method: "POST",
    body: JSON.stringify({ listId: listId }),
  }).then((_res) => {
    window.location.href = "/shopping-lists";
  });
}
