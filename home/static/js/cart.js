document.addEventListener("DOMContentLoaded", () => {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  async function updateCartItem(itemId, action) {
    try {
      const response = await fetch(`/cart/update/${itemId}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ action: action }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error:", error);
    }
  }

  function updateCartDisplay(itemRow, newQuantity, newTotal, newCartTotal) {
    itemRow.querySelector(".item-quantity").textContent = newQuantity;
    itemRow.querySelector(".item-total").textContent = `$${newTotal.toFixed(
      2
    )}`;
    document.getElementById("total-amount").textContent =
      newCartTotal.toFixed(2);
  }

  document.querySelectorAll(".quantity-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const action = e.target.classList.contains("plus")
        ? "increase"
        : "decrease";
      const itemRow = e.target.closest("tr");
      const itemId = itemRow.dataset.itemId;

      const data = await updateCartItem(itemId, action);
      if (data) {
        updateCartDisplay(
          itemRow,
          data.new_quantity,
          data.new_total,
          data.cart_total
        );
        if (data.new_quantity === 0) {
          itemRow.remove();
        }
      }
    });
  });

  document.querySelectorAll(".remove-btn").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const itemRow = e.target.closest("tr");
      const itemId = itemRow.dataset.itemId;

      const data = await updateCartItem(itemId, "remove");
      if (data) {
        itemRow.remove();
        document.getElementById("total-amount").textContent =
          data.cart_total.toFixed(2);
      }
    });
  });
});
