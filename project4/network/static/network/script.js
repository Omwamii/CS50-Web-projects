// Since code is to be ex in web-browser env & node is not set, can't import modules
// so all components will be in this file

// App component (to be rendered)
function App() {
  return (
    <div className="container">
      <Main />
    </div>
  );
}

const formatDate = (datetimeString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  const formattedDate = new Date(datetimeString).toLocaleDateString(undefined, options);
  return formattedDate;
};

// Component to create registration form
function RegForm() {
  const handleRegister = (evt) => {
    evt.preventDefault();
    const username = document.querySelector("#u-name").value;
    const password = document.querySelector("#pass").value;
    const confirmation = document.querySelector("#confirmation").value;
    const email = document.querySelector("#email").value;
    const picInput = document.querySelector("#pic")
    
    // Create a FormData object
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('confirmation', confirmation);
    formData.append('email', email);
    formData.append('pic', picInput.files[0]); // get the actual file with files

    fetch("register", {
      method: "POST",
      body: formData, // to allow file uploads, use multipart/form-data, !JSON
    })
      .then((response) => response.json())
      .then(() => window.location.reload())
      .catch((error) => console.error(error));
  };
  return (
    <div id="register">
      <h2>Register</h2>
      <form onSubmit={handleRegister} method="post">
        <div className="form-group">
          <input className="form-control" id="u-name" autoFocus type="text" name="username"
            placeholder="Username" />
        </div>
        <div className="form-group">
          <input className="form-control" id="email" type="email" name="email" 
          placeholder="Email Address" />
        </div>
        <div className="form-group">
          <input className="form-control" id="pass" type="password" name="password"
            placeholder="Password" />
        </div>
        <div className="form-group">
          <input className="form-control" id="confirmation" type="password" name="confirmation"
            placeholder="Confirm Password" />
        </div>
        <div className="input-group mb-3">
          <label className="input-group-text" htmlFor="pic">Profile picture (optional)</label>
          <input type="file" className="form-control" id="pic" />
        </div>
        <input className="btn btn-primary" type="submit" value="Register" />
      </form>
      Already have an account? <a href="{% url 'login' %}">Log In here.</a>
    </div>
  );
}

// Component to login
function Loginform() {
  const handleLogin = (evt) => {
    evt.preventDefault();
    const username = document.querySelector("#u-name").value;
    const password = document.querySelector("#pass").value;

    fetch("login", {
      method: "POST",
      body: JSON.stringify({ username: username, password: password }),
    })
      .then((response) => response.json())
      .then(() => window.location.reload())
      .catch((error) => console.error(error));
  };

  return (
    <div id="login">
      <h2>Login</h2>
      <form onSubmit={handleLogin} method="post">
        <div className="form-group">
          <input autoFocus id="u-name" className="form-control" type="text" name="username" 
          required placeholder="Username" />
        </div>
        <div className="form-group">
          <input className="form-control" id="pass" type="password" name="password" required
            placeholder="Password" />
        </div>
        <input className="btn btn-primary" type="submit" value="Login" />
      </form>
      Don't have an account? <a href="{% url 'register' %}">Register here.</a>
    </div>
  );
}

// Component with the main content on page
function Main() {
  const [user, setUser] = React.useState(null); // current user
  const [showLoginForm, setShowLoginForm] = React.useState(false);
  const [showRegisterForm, setShowRegisterForm] = React.useState(false);
  const [postType, setPostType] = React.useState("all"); // Default to 'all'
  const [posts, setPosts] = React.useState([]);
  const [nextPage, setNextPage] = React.useState(null);
  const [prevPage, setPrevPage] = React.useState(null);
  const [isEditing, setIsEditing] = React.useState(-1);
  const [showProfile, setShowProfile] = React.useState(false);
  const [currentId, setCurrentId] = React.useState(-1);
  const [loggedIn, setLoggedIn] = React.useState(false);

  const renderHomePage = () => {
    setPostType("all");
  };

  const renderFollowingPage = () => {
    setPostType("following");
  };

  React.useEffect(() => {
    // Fetch user information when the component mounts
    fetch("get_user")
      .then((res) => res.json())
      .then((data) => {
        const UserData = JSON.parse(data)
        setUser(UserData);
        setLoggedIn(UserData.is_authenticated)
      })
      .catch((err) => console.error(err));
  }, []);

  // Handle logout
  const logout = () => {
    fetch("logout")
      .then((res) => res.json())
      .then(() => {
        setLoggedIn(false)
        setShowProfile(false)
        setUser(null)
        document.querySelector(".posts").style.display = "block";
        document.querySelector("#post-new").style.display = "flex";
        document.querySelector("#post-options").style.display = 'flex'
      }) 
      .catch((err) => console.error(err));
  };

  const handleLoginClick = () => {
    setShowLoginForm(true);
    setShowRegisterForm(false);
    document.getElementById("post-section").style.display = "none"; // remove posts to login
    document.querySelector(".posts").style.display = "none";
    document.querySelector("#post-new").style.display = "none";
    document.querySelector("#post-options").style.display = 'none'
  };

  const handleRegisterClick = () => {
    setShowLoginForm(false);
    setShowRegisterForm(true);
    document.getElementById("post-section").style.display = "none";
    document.querySelector(".posts").style.display = "none";
    document.querySelector("#post-new").style.display = "none";
    document.querySelector("#post-options").style.display = 'none'
  };

  // handle post creation
  const handleSubmit = (evt) => {
    evt.preventDefault();
    const text = document.querySelector("textarea");
    
    //send API to create post
    fetch("create-post", {
      method: "POST",
      body: JSON.stringify(text.value),
    })
      .then((response) => response.json())
      .then((data) => {
        const createdPost = JSON.parse(data);
            setPosts((prevPosts) => {
                const updatedPosts = [createdPost, ...prevPosts]
                return updatedPosts;
            });
            text.value = '';
      })
      .catch((error) => console.error(error));
  };

  // scroll to new-post section when nav 'post' btn clicked
  const scrollToNewPost = () => {
    const targetSection = document.getElementById("post-new");
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: "smooth" }); // scroll to new-post section
    }
  };

  React.useEffect(() => {
    const next = nextPage ? nextPage : 1;
    fetch(`load-posts/${postType}?page=${next}`)
      .then((response) => response.json())
      .then((data) => {
        const fetchedData = JSON.parse(data);
        setPosts(fetchedData.posts);
        setNextPage(fetchedData.pagination.next);
        setPrevPage(fetchedData.pagination.previous);
      })
      .catch((error) => console.error("Error fetching posts:", error));
  }, [postType]);

  // Pagination handling
  const handleLoadMore = (type) => {
    if (type && type === "next") {
      // Fetch the next page of posts using the stored nextPage URL

      fetch(`load-posts/${postType}?page=${nextPage}`)
        .then((response) => response.json())
        .then((data) => {
          const fData = JSON.parse(data)
          setPosts(fData.posts);
          setNextPage(fData.pagination.next);
          setPrevPage(fData.pagination.previous);
        })
        .catch((error) => console.error("Error fetching next posts:", error));
    } else if (type && type === "prev") {
      // fetch previous page using set prevPage URL

      fetch(`load-posts/${postType}?page=${prevPage}`)
        .then((response) => response.json())
        .then((data) => {
          const fData = JSON.parse(data)
          setPosts(fData.posts);
          setNextPage(fData.pagination.next);
          setPrevPage(fData.pagination.previous);
        })
        .catch((error) =>
          console.error("Error fetching previous posts:", error)
        );
    }
    scrolltoTopPost(); // after next or prev page is loaded, scroll to top-most post
  };

  const scrolltoTopPost = () => {
    const targetSection = document.querySelector("div");
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: "smooth" }); // scroll to new-post section
    }
  };


  const handleLikeClick = (postId) => {
    fetch(`like-post/${postId}`)
        .then((response) => response.json())
        .then((data) => {
            // Update the like count in the local state for the specific post without reload
            const updatedPost = JSON.parse(data);
            setPosts((prevPosts) => {
                const updatedPosts = prevPosts.map((post) => {
                    if (post.id === updatedPost.id) {
                        return updatedPost;
                    }
                    return post;
                });
                return updatedPosts;
            });
            const el = document.getElementById(postId);
            el.classList.toggle("liked");
        })
        .catch((error) => console.error("Error updating like count:", error));
};

  const handleEditPost = (postId) => {
    const text = document.getElementById(`edit-${postId}`).innerText;

    fetch(`edit-post/${postId}`, { method: "POST", body: JSON.stringify(text) })
      .then((response) => response.json())
      .then((data) => {
        const updatedPost = JSON.parse(data);
            setPosts((prevPosts) => {
                const updatedPosts = prevPosts.map((post) => {
                    if (post.id === updatedPost.id) {
                        return updatedPost;
                    }
                    return post;
                });
                return updatedPosts;
            });
        setIsEditing(-1); // back to default
      })
      .catch((error) => console.error("Error updating like count:", error));
  };

  const handleEditButtonClick = (postId) => {
    setIsEditing(postId);
  };

  const gotoProfile = (userId) => {
    setCurrentId(userId);
    document.querySelector(".posts").style.display = "none";
    if (loggedIn) {
      document.querySelector("#post-new").style.display = "none";
    }
    document.querySelector("#post-options").style.display = "none";
    document.querySelector('#paginate-section').style.display = 'none';
    setShowProfile(true);
  };

  const loadHome = () => {
    setShowProfile(false)
    document.querySelector(".posts").style.display = "block";
    if (loggedIn) {
      document.querySelector("#post-new").style.display = "flex";
    }
    document.querySelector("#post-options").style.display = 'flex'
    document.querySelector('#paginate-section').style.display = 'flex'
  }

  return (
    <div className="container">
      <div id="nav-items">
        <nav>
          <ul className="navbar-nav mr-auto">
          {/* {loggedIn && (<li>
            <a>
              @{user.username}
            </a>
          </li>)} */}
            <li onClick={loadHome}>
              <a>
                <i className="fas fa-home"></i>Home
              </a>
            </li>
            <li>
              <a>
                <i className="fas fa-bell"></i>Notifications
              </a>
            </li>
            <li>
              <a>
                <i className="fas fa-envelope"></i>Messages
              </a>
            </li>
            <li>
              <a>
                <i className="fas fa-bookmark"></i>Bookmarks
              </a>
            </li>
            {loggedIn && (<li onClick={() => gotoProfile(user.id)}>
              <a>
                <i className="fas fa-user"></i>Profile
              </a>
            </li>)}
            <div id="nav-btns">
              {loggedIn  && (
                <button className="nav-btn" onClick={scrollToNewPost}>
                  Post
                </button>
              )}
              {loggedIn && (
                <button id="logout-btn" onClick={logout}>
                  Log Out
                </button>
              )}
              {!loggedIn && (
                <button className="nav-btn" onClick={handleLoginClick}>
                  Log In
                </button>
              )}
              {!loggedIn && (
                <button className="nav-btn" onClick={handleRegisterClick}>
                  Register
                </button>
              )}
            </div>
          </ul>
        </nav>
      </div>
      <div id="main-section">
        <main>
          <div id="post-options">
            <a onClick={renderHomePage} id="home">
              For you
            </a>
            {loggedIn && (
              <a onClick={renderFollowingPage} id="following">
                Following
              </a>
            )}
          </div>
          {/* Add post option on top*/}

          {loggedIn && (
            <section id="post-new">
              <div className="user-profile">
                {user && <img
                  className="profile-pic"
                  src={user.profile_pic}
                  alt="Profile pic"
                />
                }
              </div>
              <div id="form-body">
                <form method="post" onSubmit={handleSubmit}>
                  <div className="text-wrapper">
                    <textarea
                      id="text"
                      autoFocus
                      rows="4"
                      cols="50"
                      placeholder="Hi, what's on your mind today?"
                      name="text"
                      required
                    ></textarea>
                  </div>
                  <input type="submit" value="Post" />
                </form>
              </div>
            </section>
          )}
          <section id="post-section">
            {/* Load posts here */}
            <div>
              <div className="posts">
                {/* {posts} */}

                {posts.map((post) => (
                  <div key={post.id} className="post">
                    <div id="profile-pic">
                      <img
                        className="profile-pic"
                        src={post.profile_pic}
                        alt="Profile pic"
                      />
                    </div>
                    <div id="user-post">
                      <div id="post-header">
                        <strong>
                          <a onClick={() => gotoProfile(post.poster_id)}>
                            {post.poster_username}
                          </a>
                          &nbsp;&nbsp;&nbsp;{" "}
                          {post.edited && <em>{'(Edited)'}</em>}
                        </strong>
                        <strong id="post-time">{formatDate(post.time)}</strong>
                      </div>
                      <div id="post-text">
                        {isEditing === post.id && post.poster_username === user.username ? (
                          <div>
                            <div
                              id={`edit-${post.id}`}
                              className="fixedTextArea"
                              contentEditable
                              suppressContentEditableWarning
                            >
                              {post.text}
                            </div>
                            <button
                              onClick={() => handleEditPost(post.id)}
                              id="save-edit"
                              className="edit-post-btn"
                            >
                              Save edit
                            </button>
                          </div>
                        ) : (
                          <p>{post.text}</p>
                        )}
                      </div>
                      {loggedIn && isEditing !== post.id && (
                        <div id="post-actions">
                          <span>
                            <i
                              onClick={() => handleLikeClick(post.id)}
                              className={`fas fa-heart  ${post.user_liked ? 'liked' : ''}`}
                              id={post.id}
                            ></i>
                            <small>{post.like_count}</small>
                          </span>
                          <i className="fas fa-comment"></i>
                          {loggedIn && (post.poster_username !== user.username) && (
                            <i className="fas fa-bookmark"></i>
                          )}
                          {loggedIn && (post.poster_username === user.username) && (
                            <button
                              className="edit-post-btn"
                              onClick={() => handleEditButtonClick(post.id)}
                            >
                              Edit
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div id="paginate-section">
                {prevPage && (
                  <button
                    onClick={() => handleLoadMore("prev")}
                    className="page-btn"
                  >
                    Previous
                  </button>
                )}
                {nextPage && (
                  <button
                    onClick={() => handleLoadMore("next")}
                    className="page-btn"
                  >
                    Next
                  </button>
                )}
              </div>
              {showProfile && <Profile userIsLoggedIn={loggedIn} userId={currentId} />}
            </div>
          </section>
          {showLoginForm && <Loginform />}
          {showRegisterForm && <RegForm />}
        </main>
      </div>
      <div id="trends-section">
        <section id="trends">
          <div className="trend-card">{/* Trending stuff */}</div>
          <div className="follow-train">
            <h3>Who to follow</h3>
            {/* Replace with actual accounts */}
            <div id="profile">
              <div id="prof-pic">
                <img
                  className="profile-pic"
                  src="static/network/images/uhunye.jpeg"
                  alt="user-pic"
                />
              </div>
              <div id="user-info">
                <a>
                  <strong>Freedom</strong>
                </a>
                <small>@jayden_100</small>
              </div>
              <div id="prof-btn">
                <button>Follow</button>
              </div>
            </div>
            <div id="profile">
              <div id="prof-pic">
                <img
                  className="profile-pic"
                  src="static/network/images/wajackoya.jpeg"
                  alt="user-pic"
                />
              </div>
              <div id="user-info">
                <a>
                  <strong>Wamoto</strong>
                </a>
                <small>@farmer_231</small>
              </div>
              <div id="prof-btn">
                <button>Follow</button>
              </div>
            </div>
            <div id="profile">
              <div id="prof-pic">
                <img
                  className="profile-pic"
                  src="static/network/images/ojo.jpeg"
                  alt="user-pic"
                />
              </div>
              <div id="user-info">
                <a>
                  <strong>Ojo</strong>
                </a>
                <small>@samspedy112</small>
              </div>
              <div id="prof-btn">
                <button>Follow</button>
              </div>
            </div>
            <div id="profile">
              <div id="prof-pic">
                <img
                  className="profile-pic"
                  src="static/network/images/beast.jpeg"
                  alt="user-pic"
                />
              </div>
              <div id="user-info">
                <a>
                  <strong>Beast</strong>
                </a>
                <small>@mR_BeAst</small>
              </div>
              <div id="prof-btn">
                <button>Follow</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function Profile(props) {
  const [user, setUser] = React.useState(null);
  const [userPosts, setUserPosts] = React.useState([]);
  const [likedPosts, setLikedPosts] = React.useState([]);
  const [showPosts, setShowPosts] = React.useState(true); // show user's posts by default
  const [showLikedPosts, setShowLikedPosts] = React.useState(false);
  const [nextPage, setNextPage] = React.useState(null);
  const [prevPage, setPrevPage] = React.useState(null);
  const [followState, setFollowState] = React.useState(false);

  React.useEffect(() => {
    // Fetch user information when the component mounts
    fetch(`user-stats/${props.userId}`)
      .then((res) => res.json())
      .then((data) => {
        const user_data = JSON.parse(data);
        setUser(user_data);
        setLikedPosts(user_data.liked_posts);
        setUserPosts(user_data.posts);
      })
      .catch((err) => console.error(err));
  }, [!followState]);

  const loadUserPosts = () => {
    setShowPosts(true)
    setShowLikedPosts(false)
  }

  const loadLikedPosts = () => {
    setShowLikedPosts(true)
    setShowPosts(false)
  }

  const followUser = (userId) => {
    fetch(`follow/${userId}`)
      .then((res) => res.json())
      .then((data) => {
        const flag = JSON.parse(data);
        setFollowState(flag)
      })
      .catch((err) => console.error(err));
  }

  const handleLoadMore = (type) => {
    if (type && type === 'next') {
      // Fetch the next page of posts using the stored nextPage URL
      fetch(`load-posts/all?page=${nextPage}`)
        .then(response => response.json())
        .then(data => {
          setPosts(JSON.parse(data.posts));
          setNextPage(JSON.parse(data.pagination.next));
          setPrevPage(JSON.parse(data.pagination.previous))
        })
        .catch(error => console.error('Error fetching next posts:', error));
    } else if (type && type === 'prev') {
      // fetch previous page
      fetch(`load-posts/all?page=${prevPage}`)
        .then(response => response.json())
        .then(data => {
          setPosts(JSON.parse(data.posts));
          setNextPage(JSON.parse(data.pagination.next));
          setPrevPage(JSON.parse(data.pagination.previous))
    })
    .catch(error => console.error('Error fetching previous posts:', error));
  }
  scrolltoTopPost() // after next or prev page is loaded, scroll to top-most post
};

  return (
    <div className="user-profile">
    <div id="user-stats">
        <div id="profile-pic-section">
           {user && <img src={user.picture} alt="profile-picture"></img>}
        </div>
        <div id="user-follow-section" className="follow-train">
            {user && (
              <>
                <h2>{user.username}</h2>
                <div id="profile-stats">
                  <strong>Followers: {user.followers}</strong>
                  <strong>Following: {user.following}</strong>
                  {(!user.is_me && props.userIsLoggedIn) ? ((!user.is_following) ? (
                    <button onClick={() => followUser(user.user_id)} id="profile-follow-btn">Follow</button>
                  ) :
                  ( 
                    <button onClick={() => followUser(user.user_id)} id="profile-unfollow-btn" className='following'>Unfollow</button> 
                    )) : (<div></div>)}
                </div>
              </>
            )}
        </div>
    </div>
      {user && (
        <>
        <div id="post-options">
              <a id="user_posted" onClick={loadUserPosts}>
                Posts
              </a>
                <a id="user_liked" onClick={loadLikedPosts}>
                Liked posts
                </a>
            </div>
          <div id="profile-posts">
            {showPosts && (userPosts.length > 0) && (userPosts.map((post) => (
                <div key={post.id} className="post">
                  <div id="profile-pic">
                    {user && <img className="profile-pic" src={user.picture} alt="Profile pic"/>}
                  </div>
                <div id="user-post">
                  <div id="post-header">
                    <strong><a>{post.posted_by}</a>
                    </strong>
                    <strong id="post-time">{formatDate(post.time)}</strong>
                  </div>
                  <div id="post-text">
                      <p>{post.text}</p>
                  </div>
                  <div id="post-actions">
                    <span>
                      <i  className={`fas fa-heart  ${post.user_liked ? 'liked' : ''}`}></i>
                      <small>{post.like_count}</small>
                    </span>
                    <i className="fas fa-comment"></i>
                    <i className="fas fa-bookmark"></i> {/* No need to bookm if poster */}
                  </div>
                </div>
                </div>
        )))}
        {showLikedPosts && (likedPosts.length > 0) && (likedPosts.map((post) => (
                <div key={post.id} className="post">
                  <div id="profile-pic">
                    <img className="profile-pic" src={post.profile_pic} alt="Profile pic"/>
                  </div>
                <div id="user-post">
                  <div id="post-header">
                    <strong><a>{post.posted_by}</a>
                    </strong>
                    <strong id="post-time">{formatDate(post.time)}</strong>
                  </div>
                  <div id="post-text">
                      <p>{post.text}</p>
                  </div>
                  <div id="post-actions">
                    <span>
                      <i className={`fas fa-heart  ${post.user_liked ? 'liked' : ''}`}></i>
                      <small>{post.like_count}</small>
                    </span>
                    <i className="fas fa-comment"></i>
                    <i className="fas fa-bookmark"></i> {/* No need to bookm if poster */}
                  </div>
                </div>
                </div>
        )))}
      </div>
      <div id="paginate-section">
      {prevPage && <button onClick={() => handleLoadMore('prev')} className="page-btn">Previous</button>}
      {nextPage && <button onClick={() => handleLoadMore('next')} className="page-btn" >Next</button>}
      </div>
        </>
      )}
    </div>
  );
}


ReactDOM.createRoot(document.getElementById("body")).render(<App />);