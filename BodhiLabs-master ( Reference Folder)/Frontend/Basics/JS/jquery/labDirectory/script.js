$(document).ready(function () {
  // Add task
  $("#add-task").click(function () {
    const taskText = $("#task-input").val().trim();
    if (taskText) {
      $("#task-list").append(`
        <li>
          <span class="task-text">${taskText}</span>
          <div class="task-buttons">
            <button class="complete-btn">Complete</button>
            <button class="delete-btn">Delete</button>
          </div>
        </li>
      `);
      $("#task-input").val("");
    }
  });

  // Mark task as completed
  $("#task-list").on("click", ".complete-btn", function () {
    $(this).closest("li").toggleClass("completed");
  });

  // Delete task
  $("#task-list").on("click", ".delete-btn", function () {
    $(this).closest("li").remove();
  });
});

