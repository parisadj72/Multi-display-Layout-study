using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Socket : MonoBehaviour
{

    private BoxCollider boxCollider;
    void Start()
    {
        boxCollider = GetComponent<BoxCollider>();
    }

    void Update()
    {
    }

    private void OnTriggerEnter(Collider other)
    {
        print("Trigger fired");
    }
}
