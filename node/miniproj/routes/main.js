const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('sync-mysql');
const env = require('dotenv').config({ path: "../../.env" });

var connection = new mysql({
    host: process.env.host,
    user: process.env.user,
    password: process.env.password,
    database: process.env.database
});

const app = express()

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/hello', (req, res) => {
    res.send('hello world~!!')
})

// request O, query X
app.get('/select', (req, res) => {
    const result = connection.query('select * from userTbl');
    console.log(result);
    res.send(result);
})

// request O, query X
app.post('/select', (req, res) => {
    const result = connection.query('select * from userTbl');
    console.log(result);
    res.send(result);
})

// request O, query O
app.get('/selectQuery', (req, res) => {
    const userid = req.query.userid;
    const result = connection.query("select * from userTbl where userID=?", [userID]);
    console.log(result);
    res.send(result);
})

// request O, query O
app.post('/selectQuery', (req, res) => {
    const userid = req.body.userid;
    const result = connection.query("select * from userTbl where userID=?", [userID]);
    console.log(result);
    res.send(result);
})

// request O, query O
app.post('/insert', (req, res) => {
    const { id, pw } = req.body;
    const result = connection.query("insert into userTbl values (?, ?)", [id, pw]);
    console.log(result);
    res.redirect('/selectQuery?userid=' + req.body.id);
})

// request O, query O
app.post('/update', (req, res) => {
    const { id, pw } = req.body;
    const result = connection.query("update userTbl set passwd=? where userID=?", [pw, id]);
    console.log(result);
    res.redirect('/selectQuery?userid=' + req.body.id);
})

// request O, query O
app.post('/delete', (req, res) => {
    const id = req.body.id;
    const result = connection.query("delete from userTbl where userID=?", [id]);
    console.log(result);
    res.redirect('/select');
})

module.exports = app;