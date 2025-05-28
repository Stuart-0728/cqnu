// 主脚本文件

// 创建Vue应用
const app = Vue.createApp({
    data() {
        return {
            isLoggedIn: false,
            isAdmin: false,
            currentUser: null,
            toastMessage: '',
            toastTitle: '',
            toastClass: ''
        };
    },
    mounted() {
        // 检查用户登录状态
        this.checkLoginStatus();
    },
    methods: {
        // 检查用户登录状态
        async checkLoginStatus() {
            try {
                const response = await axios.get('/api/auth/profile');
                if (response.data.success) {
                    this.isLoggedIn = true;
                    this.currentUser = response.data.user;
                    this.isAdmin = this.currentUser.role === 'admin';
                }
            } catch (error) {
                console.log('未登录或会话已过期');
                this.isLoggedIn = false;
                this.currentUser = null;
                this.isAdmin = false;
            }
        },
        
        // 退出登录
        async logout() {
            try {
                const response = await axios.post('/api/auth/logout');
                if (response.data.success) {
                    this.isLoggedIn = false;
                    this.currentUser = null;
                    this.isAdmin = false;
                    this.showToast('成功', '已退出登录', 'success');
                    // 跳转到首页
                    this.$router.push('/');
                }
            } catch (error) {
                this.showToast('错误', '退出登录失败', 'error');
            }
        },
        
        // 显示通知提示
        showToast(title, message, type = 'info') {
            this.toastTitle = title;
            this.toastMessage = message;
            this.toastClass = type;
            
            const toastEl = this.$refs.toast;
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }
    }
});

// 定义组件

// 首页组件
const Home = {
    template: `
        <div class="container">
            <div class="jumbotron bg-light p-5 rounded">
                <h1 class="display-4">欢迎来到重庆师范大学师能素质协会</h1>
                <p class="lead">这里是我们协会的活动报名平台，您可以浏览和报名参加各种精彩活动。</p>
                <hr class="my-4">
                <p>立即加入我们，参与丰富多彩的校园活动！</p>
                <a class="btn btn-primary btn-lg" href="/activities" role="button">浏览活动</a>
            </div>
            
            <h2 class="mt-5 mb-4">最新活动</h2>
            <div class="row" v-if="activities.length > 0">
                <div class="col-md-4 mb-4" v-for="activity in activities" :key="activity.id">
                    <div class="card activity-card">
                        <img :src="activity.image_url || '/static/img/default-activity.jpg'" class="card-img-top activity-image" alt="活动图片">
                        <div class="card-body">
                            <h5 class="card-title">{{ activity.title }}</h5>
                            <p class="card-text">{{ truncateText(activity.description, 100) }}</p>
                        </div>
                        <div class="card-footer">
                            <small class="text-muted">活动时间: {{ formatDate(activity.start_time) }}</small>
                            <a :href="'/activities/' + activity.id" class="btn btn-sm btn-outline-primary float-end">查看详情</a>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-center py-5" v-else>
                <p>暂无活动</p>
            </div>
        </div>
    `,
    data() {
        return {
            activities: []
        };
    },
    mounted() {
        this.fetchActivities();
    },
    methods: {
        async fetchActivities() {
            try {
                const response = await axios.get('/api/activities/?status=active');
                if (response.data.success) {
                    // 只显示最新的3个活动
                    this.activities = response.data.activities.slice(0, 3);
                }
            } catch (error) {
                console.error('获取活动列表失败:', error);
            }
        },
        truncateText(text, length) {
            if (text.length <= length) return text;
            return text.substring(0, length) + '...';
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        }
    }
};

// 活动列表组件
const ActivityList = {
    template: `
        <div class="container">
            <h1 class="mb-4">活动列表</h1>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="input-group">
                        <input type="text" class="form-control" placeholder="搜索活动..." v-model="searchQuery">
                        <button class="btn btn-outline-secondary" type="button" @click="searchActivities">
                            <i class="bi bi-search"></i> 搜索
                        </button>
                    </div>
                </div>
                <div class="col-md-4">
                    <select class="form-select" v-model="statusFilter" @change="fetchActivities">
                        <option value="all">所有状态</option>
                        <option value="active">进行中</option>
                        <option value="completed">已结束</option>
                        <option value="cancelled">已取消</option>
                    </select>
                </div>
                <div class="col-md-2" v-if="isAdmin">
                    <a href="/admin/activities/new" class="btn btn-primary w-100">
                        <i class="bi bi-plus-circle"></i> 新建活动
                    </a>
                </div>
            </div>
            
            <div class="row" v-if="activities.length > 0">
                <div class="col-md-4 mb-4" v-for="activity in activities" :key="activity.id">
                    <div class="card activity-card">
                        <div class="position-absolute top-0 end-0 p-2">
                            <span class="badge bg-success" v-if="activity.status === 'active'">进行中</span>
                            <span class="badge bg-secondary" v-else-if="activity.status === 'completed'">已结束</span>
                            <span class="badge bg-danger" v-else-if="activity.status === 'cancelled'">已取消</span>
                        </div>
                        <img :src="activity.image_url || '/static/img/default-activity.jpg'" class="card-img-top activity-image" alt="活动图片">
                        <div class="card-body">
                            <h5 class="card-title">{{ activity.title }}</h5>
                            <p class="card-text">{{ truncateText(activity.description, 100) }}</p>
                            <p class="card-text">
                                <small class="text-muted">
                                    <i class="bi bi-geo-alt"></i> {{ activity.location }}
                                </small>
                            </p>
                            <p class="card-text">
                                <small class="text-muted">
                                    <i class="bi bi-calendar"></i> {{ formatDate(activity.start_time) }}
                                </small>
                            </p>
                            <p class="card-text" v-if="activity.max_participants">
                                <small class="text-muted">
                                    <i class="bi bi-people"></i> 
                                    已报名: {{ activity.registered_count }}/{{ activity.max_participants }}
                                </small>
                            </p>
                            <p class="card-text" v-else>
                                <small class="text-muted">
                                    <i class="bi bi-people"></i> 
                                    已报名: {{ activity.registered_count }} (不限人数)
                                </small>
                            </p>
                        </div>
                        <div class="card-footer">
                            <small class="text-muted">报名截止: {{ formatDate(activity.registration_deadline) }}</small>
                            <a :href="'/activities/' + activity.id" class="btn btn-sm btn-outline-primary float-end">查看详情</a>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-center py-5" v-else>
                <p>暂无活动</p>
            </div>
        </div>
    `,
    data() {
        return {
            activities: [],
            searchQuery: '',
            statusFilter: 'all',
            isAdmin: false
        };
    },
    mounted() {
        this.checkAdminStatus();
        this.fetchActivities();
    },
    methods: {
        async checkAdminStatus() {
            try {
                const response = await axios.get('/api/auth/profile');
                if (response.data.success) {
                    this.isAdmin = response.data.user.role === 'admin';
                }
            } catch (error) {
                this.isAdmin = false;
            }
        },
        async fetchActivities() {
            try {
                const response = await axios.get(`/api/activities/?status=${this.statusFilter}`);
                if (response.data.success) {
                    this.activities = response.data.activities;
                }
            } catch (error) {
                console.error('获取活动列表失败:', error);
            }
        },
        searchActivities() {
            // 简单的前端搜索实现
            if (!this.searchQuery.trim()) {
                this.fetchActivities();
                return;
            }
            
            const query = this.searchQuery.toLowerCase();
            this.activities = this.activities.filter(activity => 
                activity.title.toLowerCase().includes(query) || 
                activity.description.toLowerCase().includes(query) ||
                activity.location.toLowerCase().includes(query)
            );
        },
        truncateText(text, length) {
            if (text.length <= length) return text;
            return text.substring(0, length) + '...';
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        }
    }
};

// 登录组件
const Login = {
    template: `
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card mt-5">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">用户登录</h4>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="login">
                                <div class="mb-3">
                                    <label for="username" class="form-label">用户名</label>
                                    <input type="text" class="form-control" id="username" v-model="username" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">密码</label>
                                    <input type="password" class="form-control" id="password" v-model="password" required>
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-primary" :disabled="isLoading">
                                        <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"></span>
                                        {{ isLoading ? '登录中...' : '登录' }}
                                    </button>
                                </div>
                            </form>
                            <div class="mt-3 text-center">
                                <p>还没有账号？ <a href="/register">立即注册</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            username: '',
            password: '',
            isLoading: false
        };
    },
    methods: {
        async login() {
            this.isLoading = true;
            try {
                const response = await axios.post('/api/auth/login', {
                    username: this.username,
                    password: this.password
                });
                
                if (response.data.success) {
                    // 更新父组件的登录状态
                    this.$root.isLoggedIn = true;
                    this.$root.currentUser = response.data.user;
                    this.$root.isAdmin = response.data.user.role === 'admin';
                    
                    // 显示成功消息
                    this.$root.showToast('成功', '登录成功', 'success');
                    
                    // 跳转到首页
                    this.$router.push('/');
                }
            } catch (error) {
                let errorMessage = '登录失败';
                if (error.response && error.response.data && error.response.data.message) {
                    errorMessage = error.response.data.message;
                }
                this.$root.showToast('错误', errorMessage, 'error');
            } finally {
                this.isLoading = false;
            }
        }
    }
};

// 注册组件
const Register = {
    template: `
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card mt-5">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">用户注册</h4>
                        </div>
                        <div class="card-body">
                            <form @submit.prevent="register">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="username" class="form-label">用户名 <span class="text-danger">*</span></label>
                                        <input type="text" class="form-control" id="username" v-model="formData.username" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="email" class="form-label">邮箱 <span class="text-danger">*</span></label>
                                        <input type="email" class="form-control" id="email" v-model="formData.email" required>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="password" class="form-label">密码 <span class="text-danger">*</span></label>
                                        <input type="password" class="form-control" id="password" v-model="formData.password" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="confirmPassword" class="form-label">确认密码 <span class="text-danger">*</span></label>
                                        <input type="password" class="form-control" id="confirmPassword" v-model="confirmPassword" required>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="fullName" class="form-label">姓名 <span class="text-danger">*</span></label>
                                        <input type="text" class="form-control" id="fullName" v-model="formData.full_name" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="studentId" class="form-label">学号</label>
                                        <input type="text" class="form-control" id="studentId" v-model="formData.student_id">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="department" class="form-label">院系</label>
                                        <input type="text" class="form-control" id="department" v-model="formData.department">
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="major" class="form-label">专业</label>
                                        <input type="text" class="form-control" id="major" v-model="formData.major">
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label for="phone" class="form-label">手机号码</label>
                                    <input type="tel" class="form-control" id="phone" v-model="formData.phone">
                                </div>
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-primary" :disabled="isLoading || !isFormValid">
                                        <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"></span>
                                        {{ isLoading ? '注册中...' : '注册' }}
                                    </button>
                                </div>
                            </form>
                            <div class="mt-3 text-center">
                                <p>已有账号？ <a href="/login">立即登录</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    data() {
        return {
            formData: {
                username: '',
                email: '',
                password: '',
                full_name: '',
                student_id: '',
                department: '',
                major: '',
                phone: ''
            },
            confirmPassword: '',
            isLoading: false
        };
    },
    computed: {
        isFormValid() {
            return this.formData.username && 
                   this.formData.email && 
                   this.formData.password && 
                   this.formData.full_name && 
                   this.formData.password === this.confirmPassword;
        }
    },
    methods: {
        async register() {
            if (!this.isFormValid) {
                if (this.formData.password !== this.confirmPassword) {
                    this.$root.showToast('错误', '两次输入的密码不一致', 'error');
                } else {
                    this.$root.showToast('错误', '请填写所有必填字段', 'error');
                }
                return;
            }
            
            this.isLoading = true;
            try {
                const response = await axios.post('/api/auth/register', this.formData);
                
                if (response.data.success) {
                    this.$root.showToast('成功', '注册成功，请登录', 'success');
                    this.$router.push('/login');
                }
            } catch (error) {
                let errorMessage = '注册失败';
                if (error.response && error.response.data && error.response.data.message) {
                    errorMessage = error.response.data.message;
                }
                this.$root.showToast('错误', errorMessage, 'error');
            } finally {
                this.isLoading = false;
            }
        }
    }
};

// 定义路由
const routes = [
    { path: '/', component: Home },
    { path: '/activities', component: ActivityList },
    { path: '/login', component: Login },
    { path: '/register', component: Register }
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes
});

// 挂载路由
app.use(router);

// 挂载应用
app.mount('#app');
