output = document.getElementById('output');

let array = [1, 2, 3, 4, 5];

output.innerHTML += `Original Array: ${array}<br>`;

// Task 1: Add an Element 1 to the End of the Array
// Use the push() method to add the element 1 to the end of the array.

array.push(1);

output.innerHTML += `Array After Adding Element 1: ${array}<br>`;

// Task 2: Remove the Last Element from the Array
// Use the pop() method to remove the last element from the array.

array.pop();

output.innerHTML += `Array After Removing Last Element: ${array}<br>`;

// Task 3: Add an Element 0 to the Beginning of the Array
// Use the unshift() method to add the element 0 to the beginning of the array.

array.unshift(0);

output.innerHTML += `Array After Adding Element 0: ${array}<br>`;

// Task 4: Remove the First Element from the Array
// Use the shift() method to remove the first element from the array.

array.shift();

output.innerHTML += `Array After Removing First Element: ${array}<br>`;

// Task 5: Find the Index of Element 3 and set it to num
// Use the indexOf() method to find the index of the element 3 in the array.

let num = array.indexOf(3);

output.innerHTML += `Index of Element 3: ${num}<br>`;

// Task 6: Remove Element 3 from the Array
// Use the splice() method to remove the element 3 from the array.

array.splice(num, 1);
output.innerHTML += `Array After Removing Element 3: ${array}<br>`;

// Task 7: Add Element 6 at Index 2
// Use the splice() method to add the element 6 at index 2 in the array.

array.splice(2, 0, 6);
output.innerHTML += `Array After Adding Element 6 at Index 2: ${array}<br>`;