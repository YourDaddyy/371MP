# 371 Mini Project 1

## **Step one: Determine Requirements**

### `200 OK`:

**Description**: The request was successful, and the server returned the requested resource. The request must be valid, well-formed, and target a file that exists on the server.

**Method**: GET

**Test**: Use a valid GET request with an existing HTML to trigger the response.

**Request Message**:

``` http
GET /test.html HTTP/1.1
Host: localhost
```



### `304 Not Modified`:

**Description**: The requested resource has not been modified since the date specified in the If-Modified-Since header. The request must include an If-Modified-Since header with a timestamp. The server checks the last modified time of the requested resource. If it hasn’t been modified since that time, it returns 304 Not Modified.

**Method**: GET

**Test**: Use a GET request with the If-Modified-Since header and specify a time after the file's last modification.

**Request Message:**

```http
GET /test.html HTTP/1.1

Host: localhost

If-Modified-Since: Wed, 16 Oct 2024 07:28:00 GMT
```



### `400 Bad Request`

**Description**: The server cannot understand the request due to malformed syntax. The request must be improperly formatted, missing required components, or contain invalid syntax. This could happen if the request line or headers are incorrect.

**Method**: Any HTTP method can result in a 400 error if the syntax is invalid.

**Test**: Use an invalid or incomplete HTTP request to trigger a 400 Bad Request.

**Request Message:**

```http
GET /test.html HTTP/1.1

Host localhost
```

 

### `404 Not Found`

**Description**: The server could not find the requested resource. The request must target a resource that does not exist on the server.

**Method**: GET

**Test**: Use a valid GET request for a non-existent file.

**Request Message:**

``` http
GET /test404.html HTTP/1.1
Host: localhost
```



### `501 Not Implemented`

**Description**: The server does not support the functionality required to fulfill the request.

The request must use an HTTP method that the server does not support (for example, POST, PUT, DELETE, etc.).

**Test**: Use an unsupported HTTP method such as POST to trigger the 501 Not Implemented response.

**Request Message:**

``` http
POST /test.html HTTP/1.1
Host: localhost
```





## Step 2

### 200 Response:

![200](./src/1.png)

### 304 Response:

![304](./src/2.png)

### 400 Response:

![400](./src/3.png)

### 404 Response:

![404](./src/4.png)

### 501 Response:

![501](./src/5.png)